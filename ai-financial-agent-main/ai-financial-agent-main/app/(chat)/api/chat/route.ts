import {
  type Message,
  convertToCoreMessages,
  createDataStreamResponse,
  generateObject,
  streamText,
} from 'ai';
import { z } from 'zod';

import { auth } from '@/app/(auth)/auth';
import { customModel } from '@/lib/ai';
import { models } from '@/lib/ai/models';
import {
  systemPrompt,
} from '@/lib/ai/prompts';
import {
  deleteChatById,
  getChatById,
  saveChat,
  saveMessages,
} from '@/lib/db/queries';
import {
  generateUUID,
  getMostRecentUserMessage,
  sanitizeResponseMessages,
} from '@/lib/utils';

import { generateTitleFromUserMessage } from '../../actions';
import { AISDKExporter } from 'langsmith/vercel';

export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

export async function POST(request: Request) {
  const {
    id,
    messages,
    modelId,
    financialDatasetsApiKey,
    modelApiKey,
  }: {
    id: string;
    messages: Array<Message>;
    modelId: string;
    financialDatasetsApiKey?: string;
    modelApiKey?: string;
  } = await request.json();

  const session = await auth();

  if (!session || !session.user || !session.user.id) {
    return new Response('Unauthorized', { status: 401 });
  }

  const model = models.find((model) => model.id === modelId);

  if (!model) {
    return new Response('Model not found', { status: 404 });
  }

  if (!modelApiKey) {
    return new Response('Model API key is required', { status: 400 });
  }

  const coreMessages = convertToCoreMessages(messages);
  const userMessage = getMostRecentUserMessage(coreMessages);

  if (!userMessage) {
    return new Response('No user message found', { status: 400 });
  }

  const chat = await getChatById({ id });

  if (!chat) {
    const title = await generateTitleFromUserMessage({ message: userMessage, modelApiKey });
    await saveChat({ id, userId: session.user.id, title });
  }

  const userMessageId = generateUUID();

  await saveMessages({
    messages: [
      { ...userMessage, id: userMessageId, createdAt: new Date(), chatId: id },
    ],
  });

  return createDataStreamResponse({
    execute: async (dataStream) => {
      dataStream.writeData({
        type: 'user-message-id',
        content: userMessageId,
      });

      dataStream.writeData({
        type: 'query-loading',
        content: {
          isLoading: true,
          taskNames: []
        }
      });

      // Task breakdown using local LLM (optional enhancement)
      let taskNames: string[] = [];
      try {
        const { object } = await generateObject({
          model: customModel('gpt-4.1-nano-2025-04-14', modelApiKey),
          output: 'array',
          schema: z.object({
            task_name: z.string(),
            class: z
              .string()
              .describe('The name of the sub-task'),
          }),
          prompt: `You are a financial reasoning agent.  
          Given the following user query: ${userMessage.content}, 
          break it down to small, tightly-scoped sub-tasks 
          that need to be taken to answer the query.  
          
          Your task breakdown should:
          - Be comprehensive and cover all aspects needed to fully answer the query
          - Follow a logical research sequence from basic information to deeper analysis
          - Include 1-3 tasks maximum - fewer is better as long as they cover the complete question
          - Prioritize the most essential research steps and consolidate similar actions
          - Start with gathering fundamental data before moving to analysis and comparison
          - Make thought processes transparent to users who will see these tasks
          - Show a clear progression of reasoning that builds toward the answer
          
          Format requirements:
          - Include the ticker or company name where appropriate
          - Use present progressive tense (e.g., "Analyzing", "Retrieving", "Comparing")
          - Keep task names short (3-7 words) but specific and informative
          - Make tasks distinct with no overlap or redundancy
          - Begin with data collection tasks, then move to analysis tasks
          
          Your output will guide another LLM in executing these tasks, and users will see these steps as the system works.
          Ensure tasks are optimally structured for the available financial tools and clearly communicate the research approach.
          Focus on minimizing the number of steps while maintaining comprehensiveness.
          
          Examples of good task sequences:
          - "Retrieving AAPL financials", "Analyzing AAPL performance trends" 
          - "Finding top tech stocks", "Evaluating financial health"`,
        });
        taskNames = object.map(task => task.task_name);
      } catch (error) {
        console.warn('Task breakdown failed, continuing without tasks:', error);
      }

      // Stream the tasks in the query loading state
      dataStream.writeData({
        type: 'query-loading',
        content: {
          isLoading: true,
          taskNames
        }
      });

      let receivedFirstChunk = false;
      let fullResponse = '';
      const assistantMessages: any[] = [];

      try {
        // Fetch from Python backend SSE stream
        const pythonResponse = await fetch(`${PYTHON_API_URL}/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: userMessage.content,
            thread_id: id,
          }),
        });

        if (!pythonResponse.ok) {
          throw new Error(`Python API error: ${pythonResponse.status}`);
        }

        const reader = pythonResponse.body?.getReader();
        if (!reader) {
          throw new Error('No response body from Python API');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const eventData = JSON.parse(line.slice(6));

                if (eventData.type === 'text-delta' && eventData.content) {
                  fullResponse += eventData.content;
                  
                  if (!receivedFirstChunk) {
                    receivedFirstChunk = true;
                    dataStream.writeData({
                      type: 'query-loading',
                      content: {
                        isLoading: false,
                        taskNames: []
                      }
                    });
                  }

                  dataStream.write(eventData.content);
                } else if (eventData.type === 'tool-call') {
                  // Handle tool calls
                  dataStream.writeData({
                    type: 'tool-call',
                    content: {
                      toolName: eventData.tool_name,
                      toolInput: eventData.tool_input,
                    }
                  });
                } else if (eventData.type === 'tool-result') {
                  // Handle tool results
                  dataStream.writeData({
                    type: 'tool-result',
                    content: {
                      toolName: eventData.tool_name,
                      result: eventData.tool_result,
                    }
                  });
                } else if (eventData.type === 'message-end') {
                  // Message complete
                  break;
                }
              } catch (e) {
                console.warn('Failed to parse SSE event:', e);
              }
            }
          }
        }
      } catch (error) {
        console.error('Python API streaming error:', error);
        // Fallback: try non-streaming endpoint
        try {
          const fallbackResponse = await fetch(`${PYTHON_API_URL}/chat`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              message: userMessage.content,
              thread_id: id,
            }),
          });

          if (fallbackResponse.ok) {
            const data = await fallbackResponse.json();
            fullResponse = data.response || '';
            
            if (!receivedFirstChunk) {
              receivedFirstChunk = true;
              dataStream.writeData({
                type: 'query-loading',
                content: {
                  isLoading: false,
                  taskNames: []
                }
              });
            }

            dataStream.write(fullResponse);
          }
        } catch (fallbackError) {
          console.error('Fallback endpoint also failed:', fallbackError);
          throw error;
        }
      }

      // Save the response
      if (session.user?.id && fullResponse) {
        try {
          const assistantMessageId = generateUUID();
          
          dataStream.writeMessageAnnotation({
            messageIdFromServer: assistantMessageId,
          });

          await saveMessages({
            messages: [
              {
                id: assistantMessageId,
                chatId: id,
                role: 'assistant',
                content: fullResponse,
                createdAt: new Date(),
              },
            ],
          });
        } catch (error) {
          console.error('Failed to save chat:', error);
        }
      }
    },
  });
}

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  if (!id) {
    return new Response('Not Found', { status: 404 });
  }

  const session = await auth();

  if (!session || !session.user) {
    return new Response('Unauthorized', { status: 401 });
  }

  try {
    const chat = await getChatById({ id });

    if (chat.userId !== session.user.id) {
      return new Response('Unauthorized', { status: 401 });
    }

    await deleteChatById({ id });

    return new Response('Chat deleted', { status: 200 });
  } catch (error) {
    return new Response('An error occurred while processing your request', {
      status: 500,
    });
  }
}

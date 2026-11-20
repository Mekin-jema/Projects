Collection is a collection of openSearch nodes 
Node is one OpenSearch server

index  is similar to database tables collection

document is simllar to database row
field is similar to database table column
query   is use to send requtest for search/filter 
#  What is the difference between search and filter

Search : is used to search for a document
filter : is used to filter the result of a search
# How to create index in  openSearch  
curl -X PUT "http://localhost:9200/papers" \
  -H "Content-Type: application/json" \
# How to see the existing indices
curl -X GET "http://localhost:9200/_cat/indices?v"
# Mapping 
 - Mapping is  the most important concept in openSearch .
 - It tells openSearch what type each filed contains
    {
        "mappings":
        {
           "properties":
           {

         }

        }
    }
 




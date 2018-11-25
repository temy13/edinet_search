curl -X DELETE localhost:9200/*
curl -H "Content-Type: application/json" -X PUT  http://localhost:9200/edinet -d @mapping.json
curl -H "Content-Type: application/json" -X PUT  http://localhost:9200/edinet/_settings -d '{ "index" : { "max_result_window" : 1000000 } }'

python backend/truncate.py
python backend/scrape.py

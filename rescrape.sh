curl -X DELETE localhost:9200/*
curl -H "Content-Type: application/json" -X PUT  http://localhost:9200/edinet -d @mapping.json
curl -H "Content-Type: application/json" -X PUT  http://localhost:9200/edinet/_settings -d '{ "index" : { "max_result_window" : 1000000 } }'
rm -rf backend/data/*
python -u backend/truncate.py
python -u backend/scrape.py


python -u frontend/search_test.py

duckdb showstmp.db << EOF
CREATE TABLE shows AS 
SELECT * 
FROM read_json('py/out/*.json', 
  columns = {
    id: 'VARCHAR[]', 
    name: 'VARCHAR', 
    promotion: 'STRUCT(id BIGINT, "name" VARCHAR)', 
    arena: 'VARCHAR', 
    date: 'DATE', 
    matches: 'STRUCT(
        "type" VARCHAR, 
        result VARCHAR, 
        won DOUBLE, 
        cagematch DOUBLE, 
        wrestlers STRUCT(id BIGINT, "text" VARCHAR)[], 
        teams STRUCT(id BIGINT, "text" VARCHAR)[], 
        appearances STRUCT(id BIGINT, "text" VARCHAR)[])[]', 
    partial: 'BOOLEAN', 
    exclude: 'BOOLEAN'});
EOF

cat showstmp.db >&1  # Write output to stdout
rm showstmp.db
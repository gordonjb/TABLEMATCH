id=

while :; do
  case $1 in
    --id=?*)
      id=${1#*=} # Delete everything up to "=" and assign the remainder.
      ;;
    *)               # Default case: No more options, so break out of the loop.
      break
  esac

  shift
done

echo "${id}" > ~/idvar.txt
duckdb -csv :memory: << EOF

CREATE TABLE shows AS (
  FROM read_json('./py/out/*.json', 
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
      exclude: 'BOOLEAN'
    }
  )
);

SET VARIABLE s_id = '${id}';

COPY (
  SELECT *
  FROM shows
  WHERE list_has_all(id, CAST (getvariable('s_id') AS VARCHAR[]))
  LIMIT 1
) TO '${TMPDIR:-.}/showtable.parquet' (FORMAT 'parquet', COMPRESSION 'GZIP');

EOF

zip -r - ${TMPDIR:-.}/showtable.parquet
rm ${TMPDIR:-.}/showtable.parquet
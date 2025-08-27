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

CREATE OR REPLACE MACRO list_order_by_count(l) AS (
  array(SELECT n, FROM (SELECT unnest(l) AS n) GROUP BY n ORDER BY count(n) DESC)
);

SET VARIABLE w_id = '${id}';

COPY (
  SELECT * REPLACE (
      list_filter(matches, m -> len(list_filter(m.wrestlers, w -> w.id = getvariable('w_id'))) > 0) as matches
  )
  FROM shows
  WHERE len(list_filter(matches, m -> len(list_filter(m.wrestlers, w -> w.id = getvariable('w_id'))) > 0)) > 0
  ORDER BY date
) TO '${TMPDIR:-.}/appearancestable.parquet' (FORMAT 'parquet', COMPRESSION 'GZIP');

COPY (
  FROM (
    FROM (
      FROM (
        FROM shows
        SELECT matches, promotion
        ORDER BY date
      )
      SELECT unnest(matches, recursive := true), promotion.id AS promotionid
    )
    SELECT unnest(wrestlers, recursive := true), promotionid
  )
  SELECT id, count(id) AS count, count(DISTINCT promotionid) AS pcount, list_order_by_count(array_agg(text)) as names
  WHERE id = getvariable('w_id')
  GROUP BY id ORDER BY count DESC
) TO '${TMPDIR:-.}/statstable.parquet' (FORMAT 'parquet', COMPRESSION 'GZIP');

EOF

zip -r - ${TMPDIR:-.}/appearancestable.parquet ${TMPDIR:-.}/statstable.parquet
rm ${TMPDIR:-.}/appearancestable.parquet ${TMPDIR:-.}/statstable.parquet
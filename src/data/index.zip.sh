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
  GROUP BY id ORDER BY count DESC
) TO '${TMPDIR:-.}/wrestlertable.parquet' (FORMAT 'parquet', COMPRESSION 'GZIP');

COPY (
  FROM shows
  SELECT promotion.id as id, list_order_by_count(array_agg(promotion."name")) as names, count() as count
  GROUP BY ALL ORDER BY count DESC
) TO '${TMPDIR:-.}/promotionstable.parquet' (FORMAT 'parquet', COMPRESSION 'GZIP');

COPY (
  FROM (
    FROM shows
    SELECT matches, exclude
    ORDER BY date
  )
  SELECT unnest(matches, recursive := true)
) TO '${TMPDIR:-.}/matchtable.parquet' (FORMAT 'parquet', COMPRESSION 'GZIP');

COPY (
  FROM (
    FROM shows
    SELECT exclude
    ORDER BY date
  )
  SELECT sum(CASE WHEN exclude == true THEN 1 ELSE 0 END) AS excluded, sum(CASE WHEN exclude == false THEN 1 ELSE 0 END) AS included
) TO '${TMPDIR:-.}/statstable.parquet' (FORMAT 'parquet', COMPRESSION 'GZIP');
EOF

zip -r - ${TMPDIR:-.}/wrestlertable.parquet ${TMPDIR:-.}/promotionstable.parquet ${TMPDIR:-.}/matchtable.parquet ${TMPDIR:-.}/statstable.parquet
rm ${TMPDIR:-.}/wrestlertable.parquet ${TMPDIR:-.}/promotionstable.parquet ${TMPDIR:-.}/matchtable.parquet ${TMPDIR:-.}/statstable.parquet
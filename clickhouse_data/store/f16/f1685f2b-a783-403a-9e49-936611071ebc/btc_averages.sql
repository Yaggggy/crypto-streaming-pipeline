ATTACH TABLE _ UUID '25d45956-b970-4c45-8785-722faa99a9d7'
(
    `window_start` DateTime,
    `window_end` DateTime,
    `product_id` String,
    `average_price` Float64
)
ENGINE = MergeTree
ORDER BY window_start
SETTINGS index_granularity = 8192

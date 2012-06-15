DELETE FROM main_streamnumber;
DELETE FROM main_stream;
DELETE FROM main_interval;
DELETE FROM main_streamtype;
DELETE FROM main_streamnumbertype;

SELECT pg_catalog.setval('main_streamnumbertype_id_seq', 3, true);
SELECT pg_catalog.setval('main_streamtype_id_seq', 1, true);

INSERT INTO main_streamnumbertype (id, name, number_count) VALUES
(1, 'hour', 1),
(2, 'day', 2), -- avg over half an hour
(3, 'week', 3); -- a week dataset is avg(8 day data sets)
(4, 'month', 2); -- a week dataset is avg(8 day data sets)

INSERT INTO main_streamtype (id, name) VALUES (1, 'Default')

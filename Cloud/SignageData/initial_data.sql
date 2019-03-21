INSERT INTO public.enterprise(
	id, enterprise_name)
	VALUES (100, 'Senormatics');


INSERT INTO public.enterprise(
	id, enterprise_name)
	VALUES (101, 'Midmarket Retail');



INSERT INTO public.store(
	id, store_name, address, city, state, zipcode, enterprise_id)
	VALUES (200, 'Group Ricardo Boutique', '11 Kings Road', 'Medellin', 'Columbia', '3333', 100);

INSERT INTO public.store(
	id, store_name, address, city, state, zipcode, enterprise_id)
	VALUES (201, 'Congress Store', '6600 Congress Ave', 'Boca Raton', 'Florida', '33487', 101);



INSERT INTO public.signage(
	id, zone, store_id)
	VALUES (10, 'Entrance', 200);


INSERT INTO public.signage(
	id, zone, store_id)
	VALUES (11, 'Lobby', 201);


UPDATE public.person
	SET signage_id=11
	WHERE location = 'boca-mac-1';



	
-- add demand center
insert into demand_center 
(name, type, country, state_province, city)
values
('USA', 'clinical', 'USA', 'TX', 'Dallas')
;

-- add user
insert into public.user 
(username)
values 
('dev1')
;
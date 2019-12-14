select
    row_number() over (partition by null),
    json_object_agg(ri.description, ip.product)
from recipes as r
join recipe_ingredients as ri on ri.recipe_id = r.id
join ingredient_products as ip on ip.ingredient_id = ri.id
where r.id in (select id from recipes order by random() limit 20)
group by r.id

# Table Schema
This document describes the various tables used in the project.

## Schema Diagram
![A diagram showing the relationship between the tables](./img/table_schema.png)
Diagram created using [draw.io](https://www.draw.io)

## Table Overview
Name               | Description
------------------ | ---------------------
Potions            | The different types of potions
PotionPotency      | How much of a given stat a potion restores
PotionTypes        | Which stats are affected by potions
PotionInventory    | The amount of each potion available in the shop

### Schema
#### Potions
Column      | Type    | Description
----------- | ------- | ------------------
id          | int     | ID for the given Potion
potency_id  | int     | ForeignKey to potion's potency
type_id     | int     | ForeignKey to potion type

#### PotionPotency
Column      | Type    | Description
----------- | ------- | ------------------
id          | int     | ID for the given Potency
restores    | float   | Amount of stat restored on potion use
prefix      | varchar | Prefix to add to potion description

#### PotionTypes
Column       | Type    | Description
-----------  | ------- | ------------------
id           | int     | ID for the given PotionType
related_stat | varchar | What stat is affected by potion
color        | varchar | Color of potion

#### PotionInventory
Column       | Type    | Description
-----------  | ------- | ------------------
id           | int     | ID for the given inventory item
potion_id    | int     | ForeignKey for potion id
price        | int     | Cost of potion (in gold)
on_sale      | boolean | Whether item is currently on sale
amount       | int     | Number of potions of this type in stock

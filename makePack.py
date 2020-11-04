import mysql.connector as sql
import random

#---List of Pack names and types
#make_pack_a = Core M19 Style Pack

#Core m19 Style Pack
def make_pack_a(setN):

	#Set Set Name
	setName=setN

	#Pack properties
	pack_size = 15
	land_count = 1
	common_count = 10
	uncommon_count = 3
	r_mr_count = 1
	foil_count = 0
	rare_chance = 7
	mythic_chance = 1
	#Foil breakdown
	foil_chance = 24
	foil_common = 88
	foil_uncommon = 24
	foil_rare = 7
	foil_mythic = 1
	foil_land = 8
	foil_type = ""

	if check_foil(foil_chance):
		common_count = common_count - 1
		foil_count = 1
		print ("This pack has a foil")
		foil_type = (foil_rarity(foil_common, foil_uncommon, foil_rare, foil_mythic, foil_land))
		print (foil_type)
	else:
		print ("This pack has no foil :(")

	#Make lists of rarity types

	#Connect to DB
	#conn = sql.connect('mtg_db.db')
	conn = sql.connect(
		host="localhost",
		user="",
		password="",
		database="mtg_db"
	)

	cur = conn.cursor()

	#Mythic Rare
	cur.execute("SELECT Name, Scryfall_ID FROM Card WHERE Set_Id = %s AND Booster = 1 AND Rarity = 'mythic' AND Is_Land = 0",(setName,))
	mythic_rows = cur.fetchall()
	#Rare
	cur.execute("SELECT Name, Scryfall_ID FROM Card WHERE Set_Id = %s AND Booster = 1 AND Rarity = 'rare' AND Is_Land = 0",(setName,))
	rare_rows = cur.fetchall()
	#Uncommon
	cur.execute("SELECT Name, Scryfall_ID FROM Card WHERE Set_Id = %s AND Booster = 1 AND Rarity = 'uncommon' AND Is_Land = 0",(setName,))
	uncommon_rows = cur.fetchall()
	#Common
	cur.execute("SELECT Name, Scryfall_ID FROM Card WHERE Set_Id = %s AND Booster = 1 AND Rarity = 'common' AND Is_Land = 0",(setName,))
	common_rows = tuple(cur.fetchall())
	#Land
	cur.execute("SELECT Name, Scryfall_ID FROM Card WHERE Set_Id = %s AND Booster = 1 AND Is_Land = 1",(setName,))
	land_rows = cur.fetchall()
	booster_pack = []

	booster_pack.append(random.choices(common_rows, k=common_count))
	booster_pack.append(random.choices(uncommon_rows, k=uncommon_count))
	if check_rare_mythic(rare_chance, mythic_chance) == "rare":
		booster_pack.append(random.choice(rare_rows))
	else:
		booster_pack.append(random.choice(mythic_rows))

	if foil_count == 1 and foil_type != "land":
		cur.execute("SELECT Name, Scryfall_ID FROM Card WHERE Set_Id = %s AND Booster = '1' AND Rarity = %s AND Has_Foil = 1",(setName,foil_type))
		foil_rows = tuple(cur.fetchall())
		booster_pack.append(random.choice(foil_rows))
	elif foil_count == 1 and foil_type == "land":
		cur.execute("SELECT Name, Scryfall_ID FROM Card WHERE Set_Id = %s AND Booster = 1 AND Is_Land = 1",(setName,))
		foil_rows = cur.fetchall()
		booster_pack.append(random.choice(foil_rows))

	booster_pack.append(random.choice(land_rows))

	cur.close()
	conn.close()
	#Strip internal lists out of booster list
	output_pack = []
	for i in range(0,len(booster_pack)):
		if len(booster_pack[i]) > 2:
			for j in range(0,len(booster_pack[i])):
				output_pack.append(booster_pack[i][j])
		else:
			output_pack.append(booster_pack[i])

	out_pack = output_pack_info(pack_size, foil_count, output_pack)
	return (out_pack)

#Determine whether rare or mythic
def check_rare_mythic(r_c, m_c):
	#total chance possibility
	total_chance = r_c+m_c

	rm_value = random.randint(1,total_chance)
	if rm_value in range(1,r_c+1):
		return "rare"
	else:
		return "mythic"
#Foil Check
def check_foil(fchance):

	if random.randint(1,100) > fchance:
		return False
	else: 
		return True
#Determine foil rarity
def foil_rarity(c_c, u_c, r_c, m_c, l_c):
	
	#Total Chance possibility
	total_chance = c_c + u_c + r_c + m_c + l_c
	
	foil_value = random.randint(1,total_chance)
	print (str(total_chance) + " : " + str(foil_value)) 
	if foil_value in range(1,c_c+1):
		return "common"
	elif foil_value in range(c_c+1, c_c+u_c+1):
		return "uncommon"
	elif foil_value in range(c_c+u_c+1, c_c+u_c+r_c+1):
		return "rare"
	elif foil_value in range(c_c+u_c+r_c+1, c_c+u_c+r_c+l_c+1):
		return "land"
	else:
		return "mythic"

#This is for single foil packs
def output_pack_info(num_c, f_c, pack):

	#Last entry is num of cards, position of foil if one, total_price, empty, empty
	#Rest of entry is scryfall, num of sides, front, back or empty, price

	output_info = []
	info_entry = []
	subtotal = 0
	#Open DB to fetch and attach card Images
	conn = sql.connect(
		host="localhost",
		user="",
		password="",
		database="mtg_db"
	)


	cur = conn.cursor()

	for i in range(0,num_c):
		#Mythic Rare
		if i == 13 and f_c > 0:
			cur.execute("SELECT Scryfall_ID, Num_Sides, Front_Image, Back_Image, Price_Foil FROM Card_Images WHERE Scryfall_Id = %s", (pack[i][1],))
		else:
			cur.execute("SELECT Scryfall_ID, Num_Sides, Front_Image, Back_Image, Price FROM Card_Images WHERE Scryfall_Id = %s", (pack[i][1],))

		info_entry = cur.fetchall()
		output_info.append(info_entry)
		subtotal = subtotal + info_entry[0][4]

	#Clear info_entry
	info_entry = []
	#Create first entry
	info_entry.append(num_c)
	if f_c > 0:
		info_entry.append(num_c-1)
	else:
		info_entry.append(0)
	#Add two empty slots	
	info_entry.append(subtotal)
	info_entry.append("empty")
	info_entry.append("empty")
	#Add info_entry to output_info
	output_info.insert(0,info_entry) 
	
	cur.close()
	conn.close()
		
	return output_info
	

if __name__ == '__main__':
	make_pack_a("m19")


import os
import sqlite3

class DatabaseHandler():
    def __init__(self, database_name : str):
        self.con = sqlite3.connect(f"{os.path.dirname(os.path.abspath(__file__))}/{database_name}")
        self.con.row_factory = sqlite3.Row


    def create_person(self, discordID: str, cards: str = "", money = 0):
        cursor = self.con.cursor()
        query = f"INSERT INTO Players (discordID, cards, money) VALUES (?, ?, ?);"
        cursor.execute(query, (discordID, cards, money,))
        cursor.close()
        self.con.commit()
        
    def getcardslist(self, discordID: str) -> str:
        cursor = self.con.cursor()
        query = f"SELECT cards FROM players WHERE discordID = ?;"
        cursor.execute(query, (discordID,))
        result = cursor.fetchall()
        cursor.close()
        return dict(result[0])["cards"]
    
    def getmoney(self, discordID: str) -> str:
        cursor = self.con.cursor()
        query = f"SELECT money FROM players WHERE discordID = ?;"
        cursor.execute(query, (discordID,))
        result = cursor.fetchall()
        cursor.close()
        return dict(result[0])["money"]
    
    def add_money(self, discordID : str, newmoney):
        cursor = self.con.cursor()
        query = f"UPDATE players SET money = money + ? WHERE discordID = ?;"
        cursor.execute(query, (newmoney, discordID))
        cursor.close()
        self.con.commit()
        
    def add_money_by_sql_id(self, ID, newmoney):
        cursor = self.con.cursor()
        query = f"UPDATE players SET money = money + ? WHERE ID = ?;"
        cursor.execute(query, (newmoney, ID))
        cursor.close()
        self.con.commit()
        
    def get_ID_by_discord_ID(self, discordID):
        cursor = self.con.cursor()
        query = f"SELECT ID FROM players WHERE discordID = ?;"
        cursor.execute(query, (discordID,))
        result = cursor.fetchall()
        cursor.close()
        return dict(result[0])["ID"]
        
        
    def update_player_cards(self, discordID : str, newcards : str):
        cursor = self.con.cursor()
        query = f"UPDATE players SET cards = ? WHERE discordID = ?;"
        cursor.execute(query, (newcards, discordID))
        cursor.close()
        self.con.commit()
        
        
#    def user_exists_with(self, username: str) -> bool:
#        cursor = self.con.cursor()
#        query = f"SELECT * FROM Person WHERE username = ?;"    
#        cursor.execute(query, (username,))
#        result = cursor.fetchall()
#        cursor.close()
#        return len(result) == 1

    def less_one_card(self, cardID):
        cursor = self.con.cursor()
        query = f"UPDATE cards SET nbleft = nbleft - 1 WHERE cardID = ?;"
        cursor.execute(query, (cardID,))
        cursor.close()
        self.con.commit()
        
    def plus_one_card(self, cardID):
        cursor = self.con.cursor()
        query = f"UPDATE cards SET nbleft = nbleft + 1 WHERE cardID = ?;"
        cursor.execute(query, (cardID,))
        cursor.close()
        self.con.commit()
        
    def change_card_image(self, cardID, newimage):
        cursor = self.con.cursor()
        query = f"UPDATE cards SET image = ? WHERE cardID = ?;"
        cursor.execute(query, (newimage, cardID,))
        cursor.close()
        self.con.commit()
        
    def change_card_name(self, cardID, newname):
        cursor = self.con.cursor()
        query = f"UPDATE cards SET name = ? WHERE cardID = ?;"
        cursor.execute(query, (newname, cardID,))
        cursor.close()
        self.con.commit()
    
    def change_card_nbleft(self, cardID, newnbleft):
        cursor = self.con.cursor()
        query = f"UPDATE cards SET nbleft = ? WHERE cardID = ?;"
        cursor.execute(query, (newnbleft, cardID,))
        cursor.close()
        self.con.commit()
        
    def change_card_rarity(self, cardID, newrarity):
        cursor = self.con.cursor()
        query = f"UPDATE cards SET rarity = ? WHERE cardID = ?;"
        cursor.execute(query, (newrarity, cardID,))
        cursor.close()
        self.con.commit()


    def create_card(self, name, image, number, rarity):
        cursor = self.con.cursor()
        query = f"INSERT INTO cards (name, image, nbleft, rarity) VALUES (?, ?, ?, ?);"
        cursor.execute(query, (name, image, number, rarity,))
        cursor.close()
        self.con.commit()
        
    def getcardfromrandomID(self, cardID: int):
        cursor = self.con.cursor()
        query1 = f"SELECT nbleft FROM cards WHERE cardID = ?;"
        query2 = f"SELECT rarity FROM cards WHERE cardID = ?;"
        cursor.execute(query1, (cardID,))
        result1 = cursor.fetchall()
        nbleftresult = dict(result1[0])["nbleft"]
        cursor.execute(query2, (cardID,))
        result2 = cursor.fetchall()
        rarityresult = dict(result2[0])["rarity"]
        cursor.close()
        return (nbleftresult, rarityresult)
        
    def getcardname(self, cardID: int):
        cursor = self.con.cursor()
        query = f"SELECT name FROM cards WHERE cardID = ?;"
        cursor.execute(query, (cardID,))
        result = cursor.fetchall()
        cursor.close()
        return dict(result[0])["name"]
    
    def getcardID(self, cardname: str):
        cursor = self.con.cursor()
        query = f"SELECT cardID FROM cards WHERE name = ?;"
        cursor.execute(query, (cardname,))
        result = cursor.fetchall()
        cursor.close()
        return dict(result[0])["cardID"]
        
    def getcardimage(self, name: str):
        cursor = self.con.cursor()
        query = f"SELECT image FROM cards WHERE name = ?;"
        cursor.execute(query, (name,))
        result = cursor.fetchall()
        cursor.close()
        return dict(result[0])["image"]
    
    def getcardrarity(self, name: str):
        cursor = self.con.cursor()
        query = f"SELECT rarity FROM cards WHERE name = ?;"
        cursor.execute(query, (name,))
        result = cursor.fetchall()
        cursor.close()
        return dict(result[0])["rarity"]
    
    def getcardleft(self, name: str):
        cursor = self.con.cursor()
        query = f"SELECT nbleft FROM cards WHERE name = ?;"
        cursor.execute(query, (name,))
        result = cursor.fetchall()
        cursor.close()
        return dict(result[0])["nbleft"]
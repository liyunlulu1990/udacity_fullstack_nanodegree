#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect(database_name = "tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        conn = psycopg2.connect("dbname={}".format(database_name))
        cursor = conn.cursor()
        return conn, cursor
    except:
        print "Failed to connect to database %s" % database_name

def deleteMatches():
    """Remove all the match records from the database."""
    conn, c = connect()
    query = "truncate matches;"
    c.execute(query)
    conn.commit();
    conn.close();


def deletePlayers():
    """Remove all the player records from the database."""
    conn, c = connect()
    query = "truncate players cascade;"
    c.execute(query)
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn, c = connect()
    query = "select count(*) from players;"
    c.execute(query)
    rows = c.fetchall()
    (num,) = rows[0]
    conn.commit()
    conn.close()
    return num

	

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """

    conn, c = connect()
    query = "insert into players (name) values (%s)"
    param = (name,)
    c.execute(query, param)
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    win_query = """
    select players.id, name, count(matches.id) as wins
    from players left join matches on players.id = winner_id
    group by players.id
    order by wins desc
    """

    lose_query = """
    select players.id, name, count(matches.id) as losses
    from players left join matches on players.id = loser_id
    group by players.id
    order by losses desc
    """

    query = """
    select winners.id, winners.name, wins, wins + losses as matches
    from ({win}) as winners left join ({lose}) as losers
    on winners.id = losers.id
    """.format(win = win_query, lose = lose_query)
    
    conn, c = connect()
    c.execute(query)
    results = c.fetchall()

    conn.close()
    return results


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn, c = connect()
    query = "insert into matches (winner_id, loser_id) values (%s, %s)"
    param = (winner, loser)
    c.execute(query, param)
    conn.commit()
    c.close()
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    standings = [(record[0], record[1]) for record in playerStandings()]
    if len(standings) < 2:
        raise KeyError("Not enough players.")

    left = standings[0::2]
    right = standings[1::2]
    pairings = zip(left, right)

    results = [sum(pairing, ()) for pairing in pairings]

    return results
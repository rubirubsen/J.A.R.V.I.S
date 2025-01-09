import pyodbc

# Funktion zur Verbindung mit der MSSQL-Datenbank
def connect_to_mssql(server, database, username, password):
    try:
        # Verbindung herstellen
        connection_string = f"DRIVER={{SQL Server Native Client 11.0}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        conn = pyodbc.connect(connection_string)
        print("Verbindung erfolgreich!")
        return conn
    except pyodbc.InterfaceError as ie:
        print(f"InterfaceError bei der Verbindung zur Datenbank: {ie}")
        return None
    except pyodbc.OperationalError as oe:
        print(f"OperationalError bei der Verbindung zur Datenbank: {oe}")
        return None
    except pyodbc.DatabaseError as de:
        print(f"DatabaseError bei der Verbindung zur Datenbank: {de}")
        return None
    except Exception as e:
        print(f"Allgemeiner Fehler bei der Verbindung zur Datenbank: {e}")
        return None

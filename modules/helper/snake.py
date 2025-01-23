def create_star_pattern(n):
    for i in range(n):
        for j in range(n):
            print('*', end=' ')  
        print()  
 
def main():
    while True:
        try:
            number = input("Zahl her Arschloch (oder 'q' zum Beenden): ")
 
            if number.lower() == 'q':
                break
 
            number = int(number)
            if number <= 0:
                print("kann nur PLUS Zahlen!")
                continue
 
            create_star_pattern(number)
            print()           
        except ValueError:
            print("Was Soll das sein!")
 
if __name__ == "__main__":
    main()
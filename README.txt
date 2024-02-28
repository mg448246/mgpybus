----------------
mgpbybus
autor: Maciej Gryz
----------------
krótkie opisy dostępnych funckcji:
    >gathering:
        wszystkie funkcje wymagają apikey
        >get_bus_positions:
            jednorazowo zbiera z api inforamcje o obecnym położeniu autobusów
            dest to nazwa PLIKU
        >gather_bus_posiotions:
            cyklicznie zbiera z api inforancje o obecnym położeniu autobusów
            dest to nazwa FOLDERU
            zapisuje jako pliki w formacie json z rozszerzeniem .get_bus_positions
        >get_line_lengths:
            zbiera z api infornacje o długości tras dla każdej z linii
            każda linia ma przypisanych sobie różne trasy różnej długości, funkcja zbiera tylko tą najdłuższą
            dest to nazwa PLIKU
    >ananlyzing:
        >load_bus_positions:
            zbiera z PLIKU source inforamcje o położeniu autobusów
            pozwala określić zakres czasowy
            zwraca je jako obiekt klasy _BusLineHolder
        >load_many_positions:
            zbiera z FOLDERU source inforamcje o położeniu autobusów
            pozwala określić zakres czasowy
            zwraca je jako obiekt klasy _BusLineHolder
        >_BusLineHolder:
            umożliwia bezpośredni dostęp do pandas.DataFrame trzymającego dane o wszystkich posycjach autobusów poprzez zmienną 'df'
            >filter_by_lines:
                zwraca kopię obiektu, gdzie linia autobusu jest w liście będącej argumentem funkcji
            >filter_by_vehicle_number:
                zwraca kopię obiektu, gdzie numer autobusu jest w liście będącej argumentem funkcji
            >calculate_speed:
                zwraca obiekt klasy _BusSpeedHolder zwaierającego w wierszach dodatkową kolumnę Speed zawierającą prędkość danego
                  autobusu w okolicy danego czasu i mijesca wyrażoną w km/h
            >show_positions_on_map:
                pokazuje pozycje wszystkich pozycji autobusów na mapie
            >count_buses_per_line:
                liczy ile różnych autobusów jeżdzi każdą daną linią
                zwraca wynik jako dict postaci {"linia": liczba_autobusów}
        >_BusSpeedHolder(_BusLineHolder):
            >filter_by_speed:
                zwraca _BusSpeedHolder gdzie wszystkie prędkości mieszczą się w podanym zakresie
            >show_speed_on_map:
                pokazuje pozycje autobusów na mapie wraz z zich prędkościami
    

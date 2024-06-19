# this file scrapes data from a flixbus stop on time delays
# dataset contains: current stop and delay, previous stop location + delay, departure stop, total trip duration 

# NB: it works for the Dutch page, with small code changes it can also do for other languages

# Important note: chrome driver is ONLY compatible with the corresponding downloaded Google Chrome version.


from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By  # for locating elements
from selenium.webdriver.common.keys import Keys  # to assess search bar and enter keys, so we can type smth
import openpyxl

from selenium.webdriver.support.wait import WebDriverWait   # since pages may not load all at the same time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# function
def get_current_time_hours_minutes():
    # Get the current time
    current_time = datetime.now()
    # Return the current time in hours and minutes
    return current_time.strftime("%H:%M")


# DATA COLLECTION  OPTIONS ********************************************************************************
search_query = "Paris"  # "Gent"  #"Berlijn" # which city???
desired_stop = "Paris (Bercy Seine)" # "Gent"  # which bus stop?

data_hour = "13:59" # from which time (NB: in the same day!!!)
sleep_time = 1  # time waiting for page to load
#                          ********************************************************************************

# set up the chrome driver
PATH= "C:/Program Files (x86)/chromedriver.exe"
#driver = webdriver.Chrome(PATH)    #chrome(PATH)
options = webdriver.ChromeOptions()
#options.add_argument('--headless')
options.add_argument("--window-size=1920,1080")
cService = webdriver.ChromeService(executable_path=PATH)
driver =  webdriver.Chrome(service= cService,options=options)




# first get to the main website
driver.get('https://www.flixbus.nl/')
print(driver.title)

# flixbus may periodically update the website...
# may 2024: "9-4-0"
# june 2024: "9-11-0"
codeversion = "9-11-0" # "9-4-0"

# this only works because reisinformatie is by chance the first element
#xpath = "//a[contains(@class, 'flix-header-nav__link')]"
#travel_info_button = driver.find_element(By.XPATH, xpath)

# lets try to search with two conditions for actuele reisinformatie
xpath = "//a[contains(@class, 'flix-header-nav__link') and contains(@onclick,'emitMainNavigationClickEvent')]"
travel_info_button = driver.find_element(By.XPATH, xpath)

print(travel_info_button.text)
travel_info_button.click()
time.sleep(sleep_time)


# arrivals button (since i want to search for arrival times)
# note: by default page opens with departure times selected
# apparently this doesnt work , not sure why
class_string = "hcr-radio__input-" + codeversion


arrivals_button = driver.find_element(By.CLASS_NAME, class_string)  #hcr-radio__input-9-4-0  #horizontal-radio-arrival
print(arrivals_button.get_attribute("textContent"))
#ActionChains(driver).click(arrivals_button).perform()  # seems more robust?
ActionChains(driver).send_keys(Keys.ARROW_RIGHT).perform()
#arrivals_button.click()


# ok now we need to click on the correct bus stop (this is the desired_stop,
# but first we insert the search_query
time.sleep(sleep_time)
xpath = "//input[contains(@class, 'hcr-input__field-" + codeversion + "') and contains(@aria-label,'Station zoeken')]"
xpath_stops = "//li[@class= 'hcr-autocomplete__option-" + codeversion + "']//p[1]"
xpath_stopname = "//li[@class= 'hcr-autocomplete__option-" + codeversion + "']"
search_stop  = driver.find_element(By.XPATH, xpath)

search_stop.send_keys(search_query)
time.sleep(sleep_time)

# now lets collect the elements from the dropdown menu
stop_options = driver.find_elements(By.XPATH, xpath_stops)

n_options = len(stop_options)
print(n_options) # check how many options

# scroll to desired stop
stop_name ="muhaha"
i = 0
while stop_name != desired_stop:
    stop_name = stop_options[i].get_attribute('textContent')
    i = i + 1

# now lets click on the stop we chose
index = i - 1   # index of the correct bus stop
ActionChains(driver).move_to_element(stop_options[index]).click().perform()

# click on the search button next to the stop we chose
time.sleep(sleep_time)
xpath = "//button[contains(@class, 'hcr-btn-" + codeversion + "') and contains(@data-testid,'search-station-input-button')]"
search_button = driver.find_element(By.XPATH, xpath)  # this is the search button
ActionChains(driver).click(search_button).perform()

time.sleep(sleep_time*2)

# lets try click on arrivals button here (in the previous page it didnt work)
xpath_arrivals =   "//a[contains(@class, 'hcr-nav-horizontal__link-9-11-0') and contains(@aria-label,'Schema aankomsttijden')]"

arrivals_button2 = driver.find_element(By.XPATH, xpath_arrivals)
ActionChains(driver).move_to_element(arrivals_button2).perform()
arrivals_button2.click()

# this is the cheat code (get to the page directly)
#driver.get('https://www.flixbus.nl/track/station/dcc5426b-9603-11e6-9066-549f350fcb0c/arrivals')

print(driver.title) # check in which page we are (this prints page title)
time.sleep(sleep_time)

# xpath to different elements
xpath_button =  "//button[contains(@class, 'hcr-btn-" + codeversion + "') and contains(@aria-controls,'rides-list') ]"
xpath = "//a[contains(@class, 'hcr-list-wrapper__content-" + codeversion + "') ]"  #and contains(@data-testid,'rides-list-item')
xpath_time = "//input[contains(@class, 'hcr-input__field-" + codeversion + "') and contains(@data-testid,'time-input') ]"



bus_trips = driver.find_elements(By.XPATH, xpath)
print(len(bus_trips))
print(bus_trips[0].get_attribute(''))


# this strategy to press the button didnt really work, but its also not very precise, we may miss some bus trips by
# choosing this strategy, so its preferable to setup the clock button.

#earlier_trips_button =  driver.find_element(By.XPATH, xpath_button)
#print(earlier_trips_button.text)
# ActionChains(driver).click(earlier_trips_button).perform() does not do anything no error
# button.click() does not work returns element is not clickable
# ActionChains(driver).move_to_element(earlier_trips_button).click(earlier_trips_button) did not work

# this doesnt work in headless mode!!!
#
#ActionChains(driver).move_to_element(earlier_trips_button) ok this is not necessary even
#earlier_trips_button.click()
#driver.set_window_size(1920,1080)
#0earlier_trips_button.click()

# ok another approach is to click on time button

times  = datetime.now()
i = 0
arrival_times = []

time_check = times.strftime("%H:%M")
#print(time_check)
#print("18:54" < "23:45") : note this is true
#print("18:54" < "00:01") : note this is false
# also note that if timedelta is 20 minutes and time is higher than 23:40, the condition might never become false!!!
while time_check >= data_hour:   # <= 22:59
  times = datetime.now() - timedelta(minutes= 60*i )
  arrival_times.append(times.strftime("%H:%M"))
  time_check = arrival_times[i]
  i = i + 1

earlier_trip_clicks = len(arrival_times)
#print(len(arrival_times))
print(arrival_times)


df = pd.DataFrame(columns=['Trip Number','Bus Number', 'First Stop', 'Destination', 'Planned Time', 'Observed Time', 'Trip Status',
                           'Previous Stop','Previous Stop Time', 'Observed Previous Stop', 'Duration','Trip Duration'])

dtype = {  'Trip Number': 'int64',    'Bus Number': 'string',
    'Destination': 'string',     'Planned Time': 'bool',
    'Observed Time': 'datetime',     'Previous Stop': 'string',
    'Previous Stop Time':'datetime',     'Observed Previous Stop':'datetime',
    'Duration':'datetime',     'First Stop': 'string',     ' Trip Duration':'datetime' }


xpath = "//a[contains(@class, 'hcr-list-wrapper__content-" + codeversion + "') ]"
xpathtimes = "//strong[@class='ride-timestamp-wrapper']/time"
xpathbusnumber =  "//div[contains(@class, 'hcr-text-" + codeversion + "') ]/span"
xpath_dest = "//p/span"


for i in range(earlier_trip_clicks):
    # need to move "cursor" back to button!

   time_input = driver.find_element(By.XPATH, xpath_time)
   #if i > 0:
   # ActionChains(driver).move_by_offset(0, -100).perform()

   ActionChains(driver).move_to_element(time_input).perform()
   print('*********************')
   print(arrival_times[i])

   hour = arrival_times[i]
   time_input.send_keys(Keys.ARROW_LEFT)
   time_input.send_keys(Keys.BACKSPACE)
   time_input.send_keys(hour[:2])  #nb: works if 60 minute intervals, otherwise a bit more complex

   time.sleep(sleep_time)

    # Parse the HTML content with Beautiful Soup
   html_content = driver.page_source
   soup = BeautifulSoup(html_content, 'html.parser')
   class_string = "hcr-list-wrapper__content-" + codeversion
   bus_trips = soup.find_all('a', class_=class_string)
   print(len(bus_trips))

   #bus_numbers = driver.find_elements(By.XPATH, xpath)
   for bus_trip in bus_trips:
      class_string = "hcr-text-" + codeversion
      bus_number = bus_trip.find('div',class_ = class_string).get_text()
      destination = bus_trip.find('p').get_text()
      planned_time = bus_trip.find('strong',class_ ="ride-timestamp-wrapper").get_text()
      status = bus_trip.find('span').get_text()
      counter = len(df.index)
      if (len(planned_time)>5):
          observed_time = planned_time[5:10]
          planned_time  = planned_time[0:5]
      else:
          observed_time = planned_time
      df.loc[len(df.index)] = [counter,bus_number, 0, destination, planned_time, observed_time, status,0, 0, 0, 0, 0]

print(df.head())
print(df.tail())

# now lets collect data about previous stops before current stop  ***************************************************

# first need to go back to current time
ActionChains(driver).move_to_element(time_input).perform()
hour = arrival_times[0]  # current time
time_input.send_keys(Keys.ARROW_LEFT)
time_input.send_keys(Keys.BACKSPACE)
time_input.send_keys(hour[:2])  #nb: works if 60 minute intervals, otherwise a bit more complex
time.sleep(sleep_time)

xpath_tripbutton = "//a[contains(@class, 'hcr-list-wrapper__content-" + codeversion + "') ]"
xpath_stops  = "//div[contains(@class, 'hcr-connection__station-" + codeversion + "') ]"


counter2 = -1

for i in range(earlier_trip_clicks):
    time_input = driver.find_element(By.XPATH, xpath_time)
    # if i > 0:
    # ActionChains(driver).move_by_offset(0, -100).perform()

    ActionChains(driver).move_to_element(time_input).perform()
    print('*********************')
    print(arrival_times[i])

    hour = arrival_times[i]
    time_input.send_keys(Keys.ARROW_LEFT)
    time_input.send_keys(Keys.BACKSPACE)
    time_input.send_keys(hour[:2])  # nb: works if 60 minute intervals, otherwise a bit more complex

    time.sleep(sleep_time)

    bus_trips = driver.find_elements(By.XPATH, xpath_tripbutton)

    n_bustrips = len(bus_trips)
    #print(len(bus_trips))

    for j in range(n_bustrips):
      #ActionChains(driver).move_to_element(bus_trip).perform()

      counter2 = counter2 + 1
      # check if the bus trip occurs more than on
      #timing =  df.loc[counter2,'planned_time'] - hour
      #if timing > "00:59":
      #    break

      time.sleep(sleep_time)

      if j > 0:
          bus_trips = driver.find_elements(By.XPATH, xpath_tripbutton)
          ActionChains(driver).move_to_element(bus_trips[j]).perform()

      ActionChains(driver).click(bus_trips[j]).perform()
      time.sleep(sleep_time)

      html_content = driver.page_source
      soup = BeautifulSoup(html_content, 'html.parser')
      class_string = "hcr-connection__station-" + codeversion  # departure stations
      class_string2 = "hcr-connection__time-" + codeversion   # departure times


      bus_stops = soup.find_all('div', class_=class_string)
      bus_times = soup.find_all('div', class_=class_string2)
      bus_date = soup.find('time', {'datetime': True})
      bus_ride = soup.find('div', class_ = "ride-title") # bus number

      penultimatestop = len(bus_stops) - 2
      #time.sleep(sleep_time)
      # we are interested in penultimate stop and first stop data + bus number for linkage

      firststopdata =  bus_stops[0].get_text()
      penultimatestopdata = bus_stops[penultimatestop].get_text()
      timefirststop = bus_times[0].get_text()
      penultimatetime = bus_times[penultimatestop].get_text()
      bus_number= bus_ride.get_text()


      # remove unnecessary text and extract observed time
      substring_to_remove = "Departure time"
      substring_to_remove2 = "Arrival time"

      timefirststop = timefirststop.replace(substring_to_remove,"")
      # remove departure time OR arrival time...
      penultimatetime = penultimatetime.replace(substring_to_remove2,"")
      penultimatetime = penultimatetime.replace(substring_to_remove, "")

      if len(timefirststop)>5:
        timefirststopobserved = timefirststop[5:]
        timefirststop = timefirststop[:5]
      else:
        timefirststopobserved = timefirststop

      if len(penultimatetime) > 5:
          penultimatetimeobserved = penultimatetime[5:]
          penultimatetime  = penultimatetime[:5]
      else:
          penultimatetimeobserved = penultimatetime


      df.loc[counter2,'Previous Stop'] = penultimatestopdata
      df.loc[counter2, 'First Stop'] = firststopdata
      df.loc[counter2, 'Previous Stop Time'] = penultimatetime
      df.loc[counter2, 'Observed Previous Stop'] = penultimatetimeobserved
      fmt = "%H:%M"
      
      # duration penultimate stop to bus station of interest
      df.loc[counter2, 'Duration'] =  (datetime.strptime(df.loc[counter2, 'Observed Time'],fmt)
                                       - datetime.strptime(df.loc[counter2, 'Observed Previous Stop'],fmt))
      
      # duration departure stop to bus station of interest
      t1=  datetime.strptime(df.loc[counter2, 'Observed Time'],fmt)
      t2 = datetime.strptime(timefirststopobserved,fmt)

      # check if date of departure time is the same as current date
      datefirststop = bus_date['datetime']
      datefirststop = datefirststop[:-6]
      date_to_compare = datetime.strptime(datefirststop, "%Y-%m-%d").date()
      today_date = datetime.today().date()

      notsamedate = False

      if date_to_compare !=today_date:
          notsamedate = True

      if (t2>t1) | notsamedate:  # !need to take into account some trips start the previous day!
          t2 = t2 - timedelta(days=1)

      aux_duration = t1 - t2
      df.loc[counter2, 'Trip Duration'] = aux_duration

      # go back to previous window
      #driver.switch_to.window(original_window)  -> this doenst work but was suggested as alternative
      driver.back()

# we stopped collecting data
driver.quit()

# before printing we need to remove duplicate rows, and sort the bus trips by planned time of arrival
flixbusdf = df.drop(columns=df.columns[0])
flixbusdf = flixbusdf.drop_duplicates()
flixbusdf = flixbusdf.sort_values(by='Planned Time')

#print to excel as csv and xlsx
filenamecsv = desired_stop + f'{datetime.now():%d%m%Y_%H%M%z}'+ ".csv"
filenamexls = desired_stop + f'{datetime.now():%d%m%Y_%H%M%z}'+ ".xlsx"
flixbusdf.to_csv(filenamecsv,index=True)
#flixbusdf.to_excel(filenamexls, sheet_name=desired_stop, index=False)






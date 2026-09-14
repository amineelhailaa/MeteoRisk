from openmeteo_apiclient import OpenMeteoApi
from import_cities import filter_by_country, load_cities_from_csv

client = OpenMeteoApi()
if not client.is_api_working():
        raise RuntimeError("OpenMeteo API is not working")
    
df = load_cities_from_csv("../data/bronze/worldcities.csv")
filtered_df = filter_by_country("Morocco", df)




for index, city in filtered_df.iterrows():

        
    try:
        weather = client.get_data_from_this_city(
            latitude=city["lat"],
            longitude=city["lng"],
        )
        print(weather)

        for day in  weather["daily"]:
            
            filtered_df.at[index, "forecast_date"] = day["time"][0]
            filtered_df.at[index, "temperature_max"] = day["temperature_2m_max"][0]
            filtered_df.at[index, "temperature_min"] = day["temperature_2m_min"][0]
            filtered_df.at[index, "precipitation_sum"] = day["precipitation_sum"][0]
            filtered_df.at[index, "precipitation_probability_max"] = day["precipitation_probability_max"][0]
            filtered_df.at[index, "wind_speed_10m_max"] = day["wind_speed_10m_max"][0]
            filtered_df.at[index, "wind_gusts_10m_max"] = day["wind_gusts_10m_max"][0]
            filtered_df.at[index, "weather_code"] = day["weather_code"][0]

    except Exception as e:
        print(f"Error fetching data for {city['city']}: {e}")
    

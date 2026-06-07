import google.generativeai as genai

genai.configure(api_key="AIzaSyCR8Dcy4NO3vlAkT9-SktwBC3C8D7rz_R8")

model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content("Say hello")

print(response.text)
import streamlit as st
import requests
import yfinance as yf
import pytz
from datetime import datetime
import time
# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Home", layout="wide")

# ---------------------------------------------------------
# BACKGROUND IMAGE FROM UNSPLASH (daily refresh)
# ---------------------------------------------------------
UNSPLASH_API_KEY = st.secrets["unsplash"]["api_key"]

def get_unsplash_image():
    try:
        url = (
            "https://api.unsplash.com/photos/random?"
            "query=dark,minimal&orientation=landscape&client_id="
            + UNSPLASH_API_KEY
        )

        r = requests.get(url).json()
        print("Unsplash Response:", r)   # <–– now 'r' exists

        if "urls" in r:
            img = r["urls"]["regular"]   # faster/lighter than full
            return img + f"&t={datetime.now().timestamp()}"
        else:
            print("Unsplash ERROR: No URLs returned")
            raise Exception("No image in response")

    except Exception as e:
        print("Unsplash ERROR:", e)
        return (
            "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee"
            "?auto=format&fit=crop&w=1920&q=80"
        )

 



bg_url = get_unsplash_image()

page_bg = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: url("{bg_url}") no-repeat center center fixed;
    background-size: cover;
}}

/* -------------------------- */
/*   NEUMORPHIC CARD STYLE    */
/* -------------------------- */
.weather-card, .macro-card {{
    padding: 16px;
    border-radius: 22px;
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);

    box-shadow:
        8px 8px 16px rgba(0,0,0,0.45),
        -8px -8px 16px rgba(255,255,255,0.04);

    background-blend-mode: overlay;

    color: white;
    text-align: center;
    margin-bottom: 20px;
    transition: 0.25s ease;
}}

.weather-card:hover, .macro-card:hover {{
    transform: translateY(-3px);
    box-shadow:
        12px 12px 20px rgba(0,0,0,0.55),
        -12px -12px 20px rgba(255,255,255,0.05);
}}

/* Logo size */
.macro-logo {{
    width: 35px;
    height: 35px;
    margin-bottom: 8px;
}}
</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)

# ---------------------------------------------------------
# GREETING BASED ON IST
# ---------------------------------------------------------
def get_greeting():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    hour = now.hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 22:
        return "Good Evening"
    else:
        return "Good Evening"

greet = get_greeting()

st.markdown(
    f"<h1 style='text-align:center; color:white; margin-top:-20px;'>{greet}, Suwarn !!!</h1>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# WEATHER (OpenWeather API)
# ---------------------------------------------------------
OPENWEATHER_KEY = st.secrets["weather"]["api_key"]

cities = {
    "Pune": "1279228",
    "Mumbai": "1275339",
    "Ahmedabad": "1279233",
    "Haldwani": "1270079"
}

def get_weather(city_id):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={OPENWEATHER_KEY}&units=metric"
        data = requests.get(url).json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].title()
        icon = data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/w/{icon}.png"
        return temp, desc, icon_url
    except:
        return None, None, None

st.markdown("<h3 style='color:white;'>🌤 Weather</h3>", unsafe_allow_html=True)
w_cols = st.columns(4)

for i, (city, cid) in enumerate(cities.items()):
    temp, desc, icon = get_weather(cid)
    with w_cols[i]:
        st.markdown(
            f"""
            <div class="weather-card">
                <h4 style="margin-bottom:2px;">{city}</h4>
                {'<img src="'+icon+'" width="50">' if icon else ''}
                <div>{f"{temp:.1f}" if temp is not None else "N/A"}°C</div>
                <small>{desc if desc else ''}</small>
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------------------------------------
# MACRO INDICATORS
# ---------------------------------------------------------
# ---------------------------------------------------------
# MACRO INDICATORS (FIXED: logos + BTC/Gold/Crude prices)
# ---------------------------------------------------------
MACROS = {
    "Nifty 50": (
        "^NSEI",
        "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Nifty_50_Logo.svg/1200px-Nifty_50_Logo.svg.png"
    ),
    "Nasdaq 100": (
        "^NDX",
        "https://www.nasdaq.com/sites/acquia.prod/files/2020/09/24/nasdaq.jpg"
    ),
    "Hang Seng": (
        "^HSI",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQondjn-eCA_xCRsB7Tw3D79fmSOoTW-WXmIg&s"
    ),
    "BTC/USD": (
        "BTC-USD",
        "https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=031"
    ),
    "USD/INR": (
        "USDINR=X",
        "https://www.shutterstock.com/image-vector/vector-currency-exchange-money-conversion-260nw-2281810881.jpg"
    ),
    "Gold": (
        "GC=F",
        "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxMSEhUSExIVFRUXGBcVFRYXGBUaGBgYGBcXFxcXFRYYHSggGBolHRgXITEiJSkrLi4uFx8zODMtNygtLisBCgoKDg0OGxAQGzAlICUyLzY4LS0tLS0tLS03LzEvLy0tLy0wLS0tLS0tKy8tLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIAOMA3gMBIgACEQEDEQH/xAAcAAEAAgMBAQEAAAAAAAAAAAAAAQYDBQcEAgj/xABIEAABAgQCBgcFBQQIBgMAAAABAAIDERIhBDEFMkFhcZEGBxMiUYHRQqGxwfAjUnOC4VNicpIUFSQzQ7LC8Rc0Y4Oi0pOj4v/EABsBAQACAwEBAAAAAAAAAAAAAAADBQECBAYH/8QAMREAAgECAwYFAwMFAAAAAAAAAAECAxEEEiEFExQxUfAiQWFxkaHR4TKx8RVCUoHB/9oADAMBAAIRAxEAPwDtL3VWCMfTY5o9tNxmjG1XOaAhjabngjm1GYyRjqrHijnFpkMkBL3V2HFGvpFJz9Ue2m44I1tQqOaAhjaLngjmVGYyRjqrHijnFpkMkBL3V2HFGupFJz9Ue2m44I1tQqOaAhjaLngjmzNQy9EYarHijnEGkZeqAl5rsOKlrwBSc/VQ8U3ClrARUc/RAfLG0XPBHMmahl6Iw1WPFHOINIy9UBLzXYIHSFO3LmjxTcIGzFRz9EBDBRntQtmatmfJGGrNC6Rp2Zc0BL3VWHFGPpEjmj203HBGNqEzmgIY2i54I5tRqGXojHVWPFHOpNIyQEvdXYcUa6QpOfqj203HBGtmKjn6ICGNoueCPbVccEYarHij3U2HFAGMpueFkcyq496McXWOSPcWmQyQEvdXYcbo19IpOaPbTdueSMaHCZzQEMbRc8LI5lRqGXojDVZ2WaOcQZDJAS91dhxujX0ik5o9tN28Ea0OEzmgIY2i54WRzKjUMvRGGqzss0c4gyGSAl7q7DjdGvkKTn6o8U3ajWgio5+iAhgoueFkcyo1DL0Rhqs5HOIMhkgJe6uw43Rr5Ck5+qPFN2o1oIqOfogIYKLnhZCyZq2Z8kYatZC4g0jL1QEvNdhs8UD5CnbluujxTqoGgirbnyQEMbRc8LI5lRqGSMcXWOSOcWmQyQEvdXYcbo19IpOfqj203bnkjWgiZzQEMbRc8LI5lRqGXojDVZ3FHOINIyQEvdXYcbox1FjxsjxTdqMbVc5oA59dhxujX02PuR7Q27c+aMaHXOaAhjaLnhZHMqNQy3oxxdZ2XJHOIMhkgJe6uw43Rr6RSc/VHgNu3PmjWgiZzQEMbRc8LI5lRqHvRhqs70RziDIZICXursON0a+kUnP1R4Dbtz5o1oImc0BDG0XPCyFkzUMvfZVjGdKHOjvgQg2UN7IcR7gT33gmTQCMpAEzzJGxbRkWNKXaNHBnqSq2vtXD0Z5JN39ETKhJq5tHGuw43QPpFJz9Vq29qP8AFP8AKz5hQWxCZ9s7+WH/AOqge3cL6/H5G4l1NoxtFzwshZM1DL32Wridqc4zv5Yf/qtZoDpFEdi42CiyJYK2OAkXNtMOGUxULjepsNtWhiKm7je/r/IdCSVy0ONdhxugfIU7ct10eKdX1QNBFRz+pWVmQkMFFzt8ELJmrZnvsjDVreiFxBpGWX0UBLnV2HG6NfT3T7ke0Nu3PmjGgiZzQEMbRc8LI5lRqGXojCXWdlyRziDIZICXursON0a+kUnP1R4pu31RrQRM5oCGNoueFkc2u44XRhq1vRHuLbNy5oA1lFzwsjmVXHvRhJs7Lkj3EGTcuaAlzq7DjdGvp7pR4Dbtz5oxoImc0BDW0XPCyFlXeH1JGEus7LldHOIMhl9bUBLnV2HG6NfT3SjwG6ufNGNBEzmgIa2i54WWr6T6TGHw749p6sMHa82HrwBW0YS6zsuV1zPrK0jXHEBupCEzve4Ak+QkOa58VV3dNvzJaMM8rGh6MxzXiJkk/ZRiTtLYnePIldUhPsFyPQH/ADBb+0gxWeYbUPguk4XGygCJImTA6QzNti8ZtCPjT6lk43R68fpaHBIDyRMEiQJsM8lhw2n4UR4YwuJJIykAQJkGfFa+Lpacq4cM1hoYaqhS+mqqbQQ27cpgzGWycNjWmK2G+DDDmlwDhIgFsnCkloItwkRtzXMoeHVfVGmRG/c5UrHxew0xhYuQiAwneYLb+ZC3MHS5MQNIbIvfDNzUHNAM5bRf3hV7rG7ogRxnDiAz5H5KbBSlSxEX33c2UNGjqLRRc8LIWTNWzPkvjCRe0aHHIgOHmF9kkGQy+p3XvU7q5UkuNdhs8UD5CnbluujxTq+qACUzrfPZZZBDWUXPCyOZV3gjCTZ2XJHOIMm5ICXOrsON0a+nun6mjwG3bnzRrQRM5oCGtoueFkLKjVs9EYarOy5I5xBkMvqd0BLnV2HG6NdRY8bI8U6vqjADd2fJAHPrsOKNfTYo8AXbnzRgBu7PkgIayi54IWVd5GEnWy5I4kGTcuaAlzq7DigfT3fq6PAGrnzsjQCJnP6lZAQ1tFzwQsq7yMJOtlyRxIMm5c/egJc6uw43XKesDD04x/7zWO/8ZfJdWeANXPnZc56y4P20J59qHI/lcfULh2gr0r9GdGGfjKfop9GKw7v+oGng4FvzV90FFlBDZElpLJCXskjaVzjEuppePZcx3JwK6Bo+LTEjN2doXDg8B/zXl9oLwJ996lnBXbR74eGhgOAw7QHAhwkyRBnMEeFzbevpsEAACBDAE5C1p5yk1eDGw4jojS15a2Rqk4jkMrzImQdkpSXlgYSOOzLomRJd9pEIHhTPWBOYcTYndKvVmruX7mcpumMp1YUNuyxl8GLR9N4RiYR8wJjvSBnkfGQ2L1QYcQRTEcQARqh7neMxIgCVmkHPPxTS3fhPb4tI9yxGWSpF+xsolj6EYrt8BhzO4YATvFit6Hy7vlzVE6o8WThHw9sOI4eR73zV7ABEzrfUrL6BhpXpIpaqtNohooudvghZM1bM+SMvreWxCTOQ1fltupyMlzq7DjdA+nuo8AXbnzRgBE3Z8kBDW0XPBCyrvfVkYSdbLldHEgyGX1tQEudXYcUD6e79XR4A1c+dkaARM5/UrICGtoueFkcyu44Iwz1suSPJFm5c0ADKL57ELKr5Iwk62W+yPJB7uW66AkursLbUD6e6jwBq57r2RoBE3Z77ICA2i5vsQsq731ZGEnWy32ujiQbZe7fdASXV2FtqB9PdWGNi4TcojAf4m/MrB/W2GlN+Igg74jB81i6M2Z7A2i5vsVK6zYU2QYm9zfcPRWEdJMJ7eLw8vxYefkVWOnuncLFgBsLEQohD2kNY9rjKRBNuK5cW4yoyVyagmpp2Oe41k2OG4q24HETe137SBBf500n/ACqpOigrdaMi/Y4V37kSEfyPt7nLzeKjmpNd96FnB+JFnEZO1WvEZO2VJuzpse4xVhixLLzGMsT4q2VMGTqrxXZ4vFQTtk8Dgb/JdOLJ97zlwXFNFaQ/oukhFImC10wNtpy9yu7OsAOszDRCPCofIFeywWLpwpLO7d/cqcRQnKd4oupNdhaSVy7nlzVF/wCIf3cNL/uf/hZ8H06Dnd+BIbXB8yN8qRNdXH4f/L6P7EPDVehcgyi5vsQsq7y+cPFrAM5tImDsM8iCvpxIMm5brrsICS6uwttQPp7v1dHgDVz3XsjQCJuz+tiAgNoub7ELKu99WRhJ1st9ro4kGQy+p3QEl1dhbagdRY32o8S1c910YAdbPfZAC+u2W1A+m2aPAGrnuujADrZ77ICAyi+exCyrvZfojCTrZb7XRxM+7luQEl1dstq511y4h7cPDhNcQ0unEAJFX3QfEZ24Lor5DVz3XsuddZ8nscHzk2iqUqgJzdIHbImS5MbUyU/dpE1BXmclhwx4L3aPLWxG1tBYdawMhKxHnJbjQnRyPiYYi4eCHQzqucZZW2kLbQ+guN/ZQh5tVPOrHVFjdLmymNYseNm1hcNkj7wr8zoDjPCCPrctf0o6FR4GEixn9iQxsyBVPMC2+6xCsnJBuNuZTsJjpq3aKiTwoP3MQeURk/iFzjDRxsV66MxasNiR4djEH5XFh9xUmLpWiYhLVFgEZT2q8DYqntFR7s7j2GKsboq8xiL4dEWypmDV6eMnw375c7Ld4DDRZCJDYWggFtLTKmxAykR7ti0mnLw5+F10XoboGBiMHBiO7QktkR2jwJgkWANsl2NPdRSOepNQbbK1/V0SZJY6Zue67b5L6GHLcwR5H0V+HRDCbYRPFzz819t6J4Mf4DPOZ+aiyTfMj4mHqaboh0hZWMI6JrH7Oc7O2smbXzG+firuH093Nc46ZaOZhY2FfBaGBznMLRkXU1MMvEOAIXRYD2uaHGVwCOBuF6HZlVyp5H5d/wDDhxCTamvMkNovnsQsq731ZGEnWy32ujiZ93LdlvVkcxJdXbLagfT3fq6PkNXPdeyNAlfW9+6yAgNovnsQsrvlsRkzrZb7I8kauW66ABlF89iUVXyRk/ay3o+c+7luQEl9dstqB9Pdz/VHy9nPd4I2Uu9nvQEBtF89i5X1l4icOKfFzuQBHouqMn7WW/xXGetB9MIt3u+I/VVu0Lt016nThubLx1WwqdGYbe2fMkq1rSdCYNGAwzfCEz4BbxUzd22J/qZCrnWF/wAhGHiB8QrIqx1iO/sUTgtZO30NqKvNH5dhvLTLwsug9Xkavtof3oEUDi0B4+BXPsSJPdxKufVjFlioYOTnUH87XN9FeYyN6TZNDRljhxLBY4uJIJtsntPGyxk0zadhI5WUGLvVEoa8juuScU/7vuJ/3+Nl9MxBJkRIyv8AUliMYeK+THHit8q6GLmTGXaRuXQuqDFVYN0PbDiEeRv6rmzow8VbOp7FUxsRB8QHjy/3W1rQ/wB/ggr6xOrooUrUryndZ0P+ysijOFGhv8qpH4qx6A+0w8J08m0fyEs+S1/TjC9pgcQ3b2biOIuPgvP1e4wxMI2U7Ee9rSffUu/ZsrVWuv4/JvPWl7MtJdXbLaldPdz/AFR8vZz3eCNlLvZ781eHKQG0Xz2JRV3vdwRk/ay3+KOnO2ruy3oCS6u2W1A+i2e1Hy9nPcjJe1nvQCuu2W1K6bZo+Xs57kZL2s96Aiii+exKKu9l+iMn7WW/xWm090gbh5tY3tHgA9m1zW5zlU52U5HIE7lpOcYLNJ2RmMXJ2Ruqq7ZbVxPrgI7RzAQbgW8STP4p0o6TaQjzaZwIZtRCm2Y/efrO5gblR3Y10MCG6DW0OqbmJHPYfH4qvrVo1rZPJ3O2lRcNWfpTQ0KmBCb4MaOQC9i5BD6wtIFgowjchK4kvmH060qc4EMcvmVTZZJa2+V9yR4Wbf8AJ2FVLrGif2V43KgaQ6f6RYLmC0+EwXeTQ4n3Kk6Z6YY6MD20aY+6G285ZKWGFqVbWt8iNLdSuyuYwd8q0dCobw8RGNLiwsfIbaXAyG/NVaK8uIJl5CS6z1a6KlCDyNbvHgFZ42pkoiCuz2aE6JuxkP8ApEaJ/Ry9z/s5Fzh3jfZnmNy2rer7D+1inngxb2oBePG6VbDF5KilWlfQk8T5Hjb0DwYzjRjyCyt6EYAbYx82rDhelDHGUwt5AxdQnNY3s/NhxkjXN6G4D7kY/mC12CwbMDjWRQKWVFhcdsN4k0vAtMOtMZiXgrU2ItN0zwnaQDLOTgOObfeFspN82YXRljf0qwgzjs5rBF6bYFueIZwBmeS4bhsPAAaCwi0y5r3SnMZNM7X2lOww+fYgyJlMuaeMwZX4BdG515v4X3NuGh3/AAdkxvTvR7ob2du27SDntCpXRPTLmNpw8cyYAHFs5azi2bXC9p7PBVNmGhPAlCyn3nGwn4ysV6sFj2YZpZh21PObpW8h6rLptJ5G83x+xsqUYaeR0+D0xiQRVF7Mt8T3SeEvRbrox0sw+kHPbDJbEYAXMdtblU07RO263iuKHCRYxqivPBWXoM5uGxcJwsHHs3Hc+3xkfJdmGxM4SUZzv315nPVoRcW4qx2equ2W1K6e77+KPl7Oe7wRspX1t+e5XZXEU0Xz2JRXfLYjJ+1lvR8/Zy3ICaKL57EorvkoZP2st6PnPu5bkArrtltXF+kmGZio8SK6cy40kGRpFm+4BdX6TYsQsNEc0gEikS8Xd35z8lywBVG06zTjFe524SHORp/6ujM/u8Q+Xg7vD3rzYgx5SiwGRR4tseRVikokqxVX5o7LFOe+DlVFgHwM6fmPgsjsOKATGiPiOJohMYe8Bm6uZEh4q0RsO12YB4haTTETscDBist2OIxWGdL7kZrYwHCZU8JbzRcw5uPM0sSFDZeKR+Gw/wCd+3yWr0hja7Boa0ZNAt+q1j8SXbVLHKyhQy6vmRupfRGeBhTEiQ2DNzg33rv+hcIIMAAeAA4BcZ6HRIbcXCMQyEyAc5ONgTuzXWekXSPDwWgCI11hS1hDifCQCr9oOUpKKQSPvSukmwmkkrnWmdNuiuMjZebS2k40dxJY8DYKXLXjDxD/AIbuSjoYZR8U+ZOk1yR9sjuBmCrNoLpU6GQ19wqnGgxWy7hE/r5LPCwcUgHsyJ+JHqp6tKnOPisFdu1js2jtItitDmkEL34ttcJw8BPkuQaJfi4LqoYl4gkS87q56O6btAlFguLpSIhljgTuuCq+VFxdk7o0nTa1sUXFYN4ixGNbZrnDcBOYmdlpLG2GAZf3jvBuXmdq3uKwcSO9z3zhsJmGTmZZX32Xqw+DYwSaJfHmul1kkbammhaNe+VZpGxoWxgYNrBIBeylRSonUbBipUXBmMxccQs1KUrW4OyaLxIfBhxhetrTLwJEz75heqirvZbuCrPV9iqsNQ7/AA3ECfg7vD4u5KyunO2ruy3r09CeenGXVFPUjlk0Kq7ZbfFK6LZ7VL5eznuRkvaz3qU0IrrtltSum2al8vZz3IyXtZ70BUOsGLS2FCBzJeeAEh8TyVMkr50w0cwsOJixAwQ2SJcbETJAG+ZXJXdMcPORZEHGn4zlyK8/jqVWVduxZYeUd2b6SSWnZ0ow5zcW/wATSPfkV7YGlIT9V4PmuJ0prmjouj1ELS6Yg14DSMP9nEw+IH5muhn/AChbtrgcl5IcKo46F+0wT38TBe1w/wAxW9CWWV/b9zSotDjkNehhXnhLZwoDZZzJyaLuPABeim7HPBXRv+hWju0L4hJFPdaQSCHHMg+IEua22J6OO9l9Q8HT+IM1sei2D7PDMEpF3fPF1/hIeS20lRVsTLetxOlRViniFHg2lFAH3XCK3+SLOXkQs8DS7TZ7WHgXQnfyPm0+TgrQWry4nR0N+swHy+ajdWEv1L4N4ylHkzx4dsOIQA+gnIRRTyfdh5r1YuBDgENe7tHnKHDvwm5arFaGZBlEa5zWBzS9s5tLahUJbO7O6vjILYXbwQ1s4UUhrpCrs3AOaCdsgQJqGrFK0ou66G/ES5MqR0dGjf3n2MPYwZnj+q9uHwUOEJMaBv2nzXvjFYHLXM2reRq2YiF8ELKQvkhDBjkopWWlfTYW02H1l4rNwYQxbPROg4kd0mNyzOwcV52t8BLft/T48FY+hmLEOI5hcGh4nMmQm07SdsiVLh4xnVUZvRkdWTUW0WXo/oZsBhaCS50i53jKwAHhcraV09338ULwR3CD/D4KWylfW9+5eopwjCKjHkVMpOTuxTRfPYlFd8tihk/ay3o+fs5bluYJLKL57F58diocOG6PFeGMaJuJ2S+JOUtqzsBGtlvuuU9cGnIjYrYLAHMDQ4jKTjckb5UiewVeJUVapu438ySnDPKxXOnXSmJpB+1kBp+zh/63+Lj7svEmjRoF1txps+1CPkQfih0pAdrQyPyj5KrU6l7tFioxSsjSMgtAPdmTvIA32N/NfcCAQCTeYNFLhMGYnVSZgX2i/kVtu0wrtsv5h8V9MwsE6kaUxLWGRzGyy333VP4GToa/DaciwTKsmRltc0+4H3K0aB6VQe27SMaJwY0J4AJBD2Wy3gLRP0GDk8H63TXwzRERkyA11sp28wVHPcz9H8GcsuTKgRderReG7SNDZ95wHvXpjaDxMyeyJmZ2LT7gV7OjcF2HxDYsaFEDGzM6TnkN3+ysJ1Vkbi7uxzKLzao6pDZIADZZfUlg0fpGDHE4URrv3cnDi03XqLF5iSadmdpjkkl9yUSWAeDS8KqDEHi0/BWOLFqiPf8AtcPh43NlPyWmxLZtI3Fe/AOnCwTvvYQwv/icW/NbPWn335Gr/UjFECxELNEWOlRo3MZCNhkrw6Z03Awtojqn7ITJF35tjBxvuK59p3pPHxM2k9nC/ZsJkf4zm88bbguyhhKlXXkuppKaR0fA6RgxXxYcJ4e6FDdEcQJsEpANnPvGZGVvgvcGbcz4+ngOCp/VlBlCxET7zHN/+3DD/UVdFFiIKnPLERbZEl8uMhOU5XkvtQVAbHxonFRYhL5NayZlKdR85yt9SW7bpOLDBcYrgBczMxbitVo/Egw2yEwBKbS11hacmmYtsktD0k0kY7m4WAT3tY3HGc9gWKeeVS0HZej5GZJW1Reeg3S+Njo8WE9o7NonDiSkahm0gWNr7pbZ2u5fRbPaqF0VwTcN2bG7CAT4k2JPNX5khrZ77r0+Ar72Dv5P6FXiIqMtCA+u2W1cI6fYntMXGM5gOLRwbYe4Bd4eQdXPdZVKP1eYJ5Ln9rUTM9/9FJiaU6llEUZxg22cMMNfBgjwXcB1ZYH2hFA/E/RQerHAnIRiPxP0UHC1PQm4iBw12HHgsTsGPBd3d1Y4A6vbE/ieoQdWOA29tP8AE/RbcPU6jfwOC/0SWRI4Er6aIgyiPHmV3YdV+BGsIwH4n6Ieq7AnIRiPxP0WeHqehjfwOGjFxx7c+ICyN0vHGYaeYXbndV2jzq9sT+J+igdVuj9vbT/E/Ra8I3zSM8SvU4g/SdV3QRPxaZEbxZbDA9LIkK03ub92IA7/AMs114dVeA9oRgPxPQKD1U6POQjS/E57Fh4JSVmkZ4lFBwPTLDPtEnDPjmPflzK3+GLIonCiMiD90ifLNb13VPo46ojH/ueoX1B6qtHMMwY7XbopB3XAXNPZV/0u31MrFxK9GgkTBC+tGH+yYQ/ciYmH/M+oK94PotChilz4zm7BEc13vpmvtnRiAG0Na4MqLxcWcRIuExmof6ZXs1p8/gy8TB2KBiIrWCb3Ug5Da6X3W5n4DbJVLpB0iikFkGcJuRcP7w/mFmflvvXY4/QvCvnLtCSGhxquaagHTIz7xFrZWstdF6ssA7W7afh2n6KWjs2cXeVjbiqdtbn52cZ557eO33ryR7L9D/8AB3RsyXCOJ/8AVPyCh3U5o07I5b49rz2K0jSaIHXiyl9A8PTo8n7wB/mjwT/pVikrlg+hmFhQhBhdpSJCRdeTXVC5His46MYcAgl7XHaCJjeJgiap6uza85t6at+fr7E3FU0c90hpCFAl2jpOdqsF3u4DYN5stHpd0WMJToZ9xv8AqObvhuV/h9VOAEQxnnEF5uXOjFxJ32W3d0LwxyDyP4v0Wz2ZUg04NP3N6eLpf3JnCsdAiQ2FzXuBGUlftAwGgssP7iA8HbVEgsdEM8+866t2L6vcFEaW/amecny+S2GF6K4eHICsEMZDAqn3YbQ1mzOQC2qYCtKFtL9+hpPFU29Lle7SSvUH7Rof4gfCfzWrHR6F7VY/N+i2UODS1rWTpaABfw8V0bPwtWg5Z7WZzVqkZ2sZSyi4vsQMquoYCLuy5o8EmbcuSsznDX12NtqF9PdUvIOrnyRpAEnZ80ALaLi+xAyrvfVlDARrZc7o4EmYy+tiAB1djbahfT3VLyDq58kaQBJ2fP3oAW0XF9iBlXe+rKGAjWy53RwJMxl9TsgAdXY22oX0936upeQdXPkjSAJHP6ldACKLi+xAyrvfVlDBLW9UcCTMZfU7IAHV2NtqF9Pd+rqXmernyRpAEjn9SugBFFxfYgZPvefJQwS1vVCCTMav1OyAA12NpJXLueXNS8z1fPYgIlI63z2XQAtouL7EDKu8oYCLuy5o4EmbcuSANdXY22oX0936upeQdXPlZGkASOf1tQAtouL7EDKu99WUMBGtlzRwJMxl9TsgAdXY22oXUWF9ql5nq58kYQLOz5oD6xOXmmH1URAYsLn5JH1uSIgMmKy8/VTA1eaIgMeFz8lEfW5IiAyYrLz9VMHV5qUQGLC5+SiLr8kRAZMVkOKmDq8/mpRAYsLmeCiLrckRAZMVkOKmHqeR+aIgPjC5lfL9fzHyREBlxOXmmH1ealEBhwufl6JH1uSIgMmKy81MHV5oiAx4XM8FGJz8kRAf/9k="
    ),
    "Crude Oil": (
        "CL=F",
        "data:image/jpeg;base64,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"
    )
}


def fetch_macro(ticker):
    try:
        # First attempt - 2 day history
        data = yf.Ticker(ticker).history(period="2d")
        if len(data) >= 2:
            last = data["Close"].iloc[-1]
            prev = data["Close"].iloc[-2]
            pct = (last - prev) / prev * 100
            return last, pct

        # Fallback 1 — use fast_info
        t = yf.Ticker(ticker)
        last = t.fast_info.get("last_price")
        prev = t.fast_info.get("previous_close")

        if last and prev:
            pct = (last - prev) / prev * 100
            return last, pct

        # Fallback 2 — as last resort
        return None, None

    except:
        return None, None

st.markdown("<h3 style='color:white; margin-top:25px;'>📈 Macro Indicators</h3>", unsafe_allow_html=True)
m_cols = st.columns(len(MACROS))

for i, (name, (ticker, logo)) in enumerate(MACROS.items()):
    val, pct = fetch_macro(ticker)

    val_fmt = "N/A" if val is None else f"{val:,.2f}"
    pct_fmt = "" if pct is None else f"{pct:+.2f}%"
    pct_color = "lightgreen" if pct and pct > 0 else "salmon"

    with m_cols[i]:
        st.markdown(
            f"""
            <div class="macro-card">
                <img src="{logo}" class="macro-logo">
                <br><b>{name}</b><br>
                {val_fmt}<br>
                <span style="color:{pct_color};">{pct_fmt}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

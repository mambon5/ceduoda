import requests

def obtenir_geo(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,zip,lat,lon,isp,org,as")
        data = r.json()

        if data.get("status") != "success":
            return None

        return {
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "ciutat": data.get("city"),
            "regio": data.get("regionName"),
            "pais_fisic": data.get("country"),
            "codi_pais_fisic": data.get("countryCode"),
            "zip": data.get("zip"),
            "isp": data.get("isp"),
            "org": data.get("org"),
            "as_name": data.get("as"),
        }
    except:
        return None
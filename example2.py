from requests import request
import json


def Run(engine):
    bd = engine.body
    bd_dict = json.loads(bd)

    if "hookConfig" in bd_dict:
        engine.result.set({"Result": "Ok"}, status_code=200, content_type="json")
        return None
    else:
        order_id = bd_dict["OrderId"]
        order_status = bd_dict["State"]
        order_domain = bd_dict["Domain"]

        token_flow = "Token TOKEN_WENI"
        flow_uuid = "flow_uuid"

        vtex_json = get_order_data(order_id, token_flow)
        uuid = create_contact(vtex_json, token_flow, order_status=order_status, order_domain=order_domain)
        status_code, response = flow_start(uuid, token_flow, flow_uuid)

        engine.result.set(response, status_code=status_code, content_type="json")
        return None


def get_global_data(token):
    url = "https://flows.weni.ai/api/v2/globals.json?key=x_vtex_api_appkey"

    headers = {
        'Authorization': token
    }

    response = request("GET", headers=headers, url=url)
    response = response.json()

    vtex_app_key = response["results"][0]["value"]

    url = "https://flows.weni.ai/api/v2/globals.json?key=x_vtex_api_apptoken"
    response = request("GET", headers=headers, url=url)
    response = response.json()

    vtex_app_token = response["results"][0]["value"]

    url = "https://flows.weni.ai/api/v2/globals.json?key=url_api_vtex"
    response = request("GET", headers=headers, url=url)
    response = response.json()

    url_api_vtex = response["results"][0]["value"]

    return url_api_vtex, vtex_app_token, vtex_app_key

def get_order_data(order_id: str, token):
    url_api_vtex, vtex_app_token, vtex_app_key = get_global_data(token)

    url = f'{url_api_vtex}/api/oms/pvt/orders/{order_id}'

    headers = {
        'X-VTEX-API-AppToken': f'{vtex_app_token}',
        'X-VTEX-API-AppKey': f'{vtex_app_key}'
    }

    response = request("GET", url=url, headers=headers)
    response = response.json()

    return response

def create_contact(vtex_data, token, order_status, order_domain):
    phone = vtex_data['clientProfileData'].get("phone").replace("+", "")
    name = f'{vtex_data["clientProfileData"].get("firstName")} {vtex_data["clientProfileData"].get("lastName")}'
    document = vtex_data['clientProfileData'].get("document")
    email = vtex_data['clientProfileData'].get("email")
    order_id = vtex_data.get("orderId")
    order_form_id = vtex_data.get("orderFormId")
    selected_address = f'{vtex_data["shippingData"]["selectedAddresses"][0]["street"]} - {vtex_data["shippingData"]["selectedAddresses"][0]["number"]} - {vtex_data["shippingData"]["selectedAddresses"][0]["neighborhood"]} - {vtex_data["shippingData"]["selectedAddresses"][0]["city"]} - {vtex_data["shippingData"]["selectedAddresses"][0]["state"]}'
    geo_coordinates = vtex_data["shippingData"]["selectedAddresses"][0]["geoCoordinates"]
    shipping_estimated_date = vtex_data["shippingData"]["logisticsInfo"][0]["shippingEstimateDate"]
    sellers = vtex_data["sellers"][0]["name"]

    url = f"https://flows.weni.ai/api/v2/contacts.json?urn=whatsapp:{phone}"

    payload = json.dumps({
        "name": f"{name}",
        "fields": {
            "email": email,
            "phone": phone,
            "orderid": order_id,
            "sellers": sellers,
            "document": document,
            "state": order_status,
            "shippingestimatedate": shipping_estimated_date,
            "selectedaddresses": selected_address,
            "geocoordinates": f"{geo_coordinates}",
            "orderformid": order_form_id,
            "domain": order_domain
        }
    })
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    response = request("POST", url=url, headers=headers, data=payload)
    response = response.json()

    uuid = response['uuid']

    return uuid


def flow_start(contact_uuid, token, flow_uuid):
    url = "https://flows.weni.ai/api/v2/flow_starts.json"

    headers = {
        'Authorization': token,
        'Content-type': 'application/json'
    }

    payload = json.dumps({
        "flow": f"{flow_uuid}",
        "contacts": [f"{contact_uuid}"]
    })

    response = request("POST", url=url, headers=headers, data=payload)
    status_code = response.status_code
    response = response.json()

    return status_code, response
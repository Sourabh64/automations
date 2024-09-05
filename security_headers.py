# import requests
# import json
#
# urls = ['api.payu.in', 'blog.payubiz.in', 'cbjs.payu.in', 'chargeback.payu.in', 'corporate.payu.in', 'info.payu.in', 'info3.payu.in', 'integration-facebook.payu.in', 'jssdk.payu.in', 'newstatic.payu.in', 'notification.payu.in', 'oneapi.payu.in', 'pay.webfront.in', 'payments.cdn.globalpayments.co.in', 'pns.payu.in', 's.payu.in', 'scan.payu.in', 'securepayments.payu.in', 'secureproxy.payu.in', 'solutions.payu.in', 'staticapi.payu.in', 'tax.payu.in', 'taxnet.payu.in', 'tools.payu.in', 'tsp.payu.in', 'vpp.payu.in', 'web-assets.payu.in', 'webfront.payu.in', 'webfrontapp.payu.in', 'widget.payu.in', 'www.payu.in']
#
# for url in urls:
#     url = 'https://'+url
#     try:
#         resp = requests.get(url)
#         # print(resp.headers)
#         headers = resp.headers
#         if 'Server' in headers:
#             server = headers['Server'].split("/")[-1]
#             # print("Server")
#             # print(url, server)
#         if 'X-Powered-By' in headers:
#             server2 = headers['X-Powered-By'].split("/")[-1]
#             # print("X-Powered-By")
#             # print(url, server2)
#         if 'X-Content-Type-Options' not in headers:
#             print(url)
#         if 'Strict-Transport-Security' not in headers:
#             print(url)
#     except Exception as e:
#         print(url, str(e))


def compare_json(static_json, response_json, custom_messages=None, path=""):
    """
    Compare two JSON objects and print mismatched values with customized messages.

    Args:
        static_json (dict): The static JSON object.
        response_json (dict): The JSON object from the API response header.
        custom_messages (dict): A dictionary of custom messages for mismatched headers.
        path (str): The current path being compared (for nested dictionaries).
    """
    if custom_messages is None:
        custom_messages = {}

    # Both are dictionaries
    if isinstance(static_json, dict) and isinstance(response_json, dict):
        all_keys = set(static_json.keys()).union(response_json.keys())

        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            if key not in response_json:
                print(custom_messages.get(key, f"Key '{new_path}' is missing in the response JSON."))
            elif key not in static_json:
                print(custom_messages.get(key, f"Key '{new_path}' is missing in the static JSON."))
            else:
                # Recursively compare nested structures
                compare_json(static_json[key], response_json[key], custom_messages, new_path)

    # Both are lists
    elif isinstance(static_json, list) and isinstance(response_json, list):
        min_length = min(len(static_json), len(response_json))
        for index in range(min_length):
            new_path = f"{path}[{index}]"
            compare_json(static_json[index], response_json[index], custom_messages, new_path)

        # Handle list length mismatch
        if len(static_json) != len(response_json):
            print(f"List length mismatch at '{path}': {len(static_json)} != {len(response_json)}")

    # Compare values directly
    else:
        if static_json != response_json:
            print(custom_messages.get(path,
                                      f"Mismatch at '{path}': Static JSON = {static_json}, Response JSON = {response_json}"))


# Example usage with customized messages
static_json = {
    "Strict-Transport-Security": "max-age=15768000; includeSubdomains; preload",
    "Content-Security-Policy": "default-src 'self'",
    "X-Frame-Options": "deny",
    "X-XSS-Protection": "1; mode=block",
    "X-Content-Type-Options": "nosniff",

    
}

response_json = {
    "Content-Type": "application/xml",
    "Content-Length": "1024",
    "Authorization": "Bearer token456",
    "Custom-Header": "some_value"
}

# Custom messages for mismatches
custom_messages = {
    "Content-Type": "Content-Type mismatch: Expected 'application/json', but got a different type.",
    "Authorization": "Authorization token does not match.",
    "Custom-Header": "Unexpected header 'Custom-Header' found in response."
}

compare_json(static_json, response_json, custom_messages)

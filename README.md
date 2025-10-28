# Wialon SDK for Python

[![pypi version](https://badge.fury.io/py/wialon.svg)](https://pypi.org/project/wialon/)

## Introduction

Wialon SDK for Python is a library that provides an easy way to interact with the Wialon Remote API. It allows developers to integrate Wialon functionalities into their Python applications seamlessly. Uses python property `__getattr__` to dynamically call Wialon Remote API methods, converting snake_case method names to svc format (e.g., core_login -> core/login).

## Token generation

The library does not generate Wialon tokens. To generate a token, you can use our [Wialon Token Generator](https://developers.layrz.com/tools/wialon-token-generator).

## Disclaimer

This library is not an official Wialon product, it's developed by Golden M, Inc as a third-party SDK to interact with Wialon Remote API. For direct support of the responses of the Remote API, please contact Gurtam support.

## Usage

```python
from wialon.sdk import WialonSdk, WialonError, SdkException, AsyncWialonSdk

# Initialize Wialon instance
sdk = WialonSdk()
# Or for async usage
sdk = AsyncWialonSdk()

try:
  token = os.getenv('WIALON_TOKEN')
  response = sdk.login(token)
  # Or async usage
  response = await sdk.login(token)
  print(response)

  parameters = {
    'spec':{
      'itemsType': str,
      'propName': str,
      'propValueMask': str,
      'sortType': str,
      'propType': str,
      'or_logic':bool
    },
    'force': int,
    'flags': int,
    'from': int,
    'to': int
  }

  units = sdk.core_search_items(parameters)
  # Or async usage
  units = await sdk.core_search_items(parameters)

  sdk.logout()
  # Or async usage
  await sdk.logout()
except SdkException as e:
  print(f'Sdk related error: {e}')
except WialonError as e:
  print(f'Wialon related error: {e}')
except Exception as e:
  print(f'Python error: {e}')
```

## Methods available

For more information, please go to [Wialon Remote API documentation](https://help.wialon.com/en/api/user-guide)

## Who are you?

Golden M is a software/hardware development company what is working on a new, innovative and disruptive technologies. Experts on integrating Wialon products since 2016 with custom hardware and software solutions. To work with us, contact us at [sales@goldenm.com](mailto:sales@goldenm.com).

## Contributing

Merge requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

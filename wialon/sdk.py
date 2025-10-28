import json
import logging
from collections.abc import Callable
from typing import Any, Self, cast

import requests
from pydantic import BaseModel, Field

from wialon.exceptions import SdkException, WialonError

log = logging.getLogger('wialon.sdk')


class WialonSdk(BaseModel):
  """Sdk handler"""

  url: str = Field('https://hst-api.wialon.com', description='Base URL to perform any request')
  session_id: str = Field('', description='Wialon session ID, keep empty to login later')
  default_params: dict[str, Any] = Field(default_factory=dict, description='Base parameters to use')
  user_id: str = Field('', description='Wialon user ID, filled after login')

  @property
  def base_url(self: Self) -> str:
    return f'{self.url}/wialon/ajax.html?'

  def call(self: Self, *, method: str, args: dict[str, Any] | list[Any]) -> dict[str, Any] | list[Any]:
    """
    Call method
    Allows to call any method in the Remtoe API using the following rule:
    To get the SVC, uses the default __getattr__ method to convert the Remote API SVC to a flat
    method in Python, for example:
    core/search_items -> core_search_items

    :param method: defines the method to call
    :param args: defines the arguments to use, must be a dict, in case if the method requires a list,
                 the default_params will be ignored

    :return: the response from the server, must be a dict or a list
    :raises SdkException: if any error occurs
    :raises WialonError: if the server returns an error
    """
    svc = None

    if method == 'unit_group_update_units':
      svc = 'unit_group/update_units'
    else:
      svc = str(method).replace('_', '/', 1)

    parameters = {'svc': svc, 'sid': self._session_id}

    if isinstance(args, list):
      try:
        parameters['params'] = json.dumps(args)
      except Exception as e:
        raise SdkException(f'Internal error: {e}') from e
    else:
      try:
        arguments: dict[str, Any] = {}
        arguments.update(self.default_params)
        arguments.update(args)
        parameters['params'] = json.dumps(arguments)
      except Exception as e:
        raise SdkException(f'Internal error: {e}') from e

    url = self.base_url
    for key, value in parameters.items():
      url += f'{key}={value}&'

    log.debug(
      'Call method: %s - svc: %s - params: %s - sessionId: %s',
      method,
      svc,
      parameters.get('params', ''),
      self._session_id,
    )
    log.debug('Call url: %s', url)

    try:
      request = requests.post(url=url)
    except Exception as e:
      raise SdkException(f'Internal error: {e}') from e

    try:
      response = request.json()
    except Exception as e:
      raise SdkException(f'Internal error: {e}') from e

    if 'error' in response and response['error'] != 0:
      reason = ''
      if 'reason' in response:
        reason = response['reason']

      raise WialonError(code=response['error'], reason=reason)

    return cast(dict[str, Any], response)

  def login(self: Self, token: str) -> dict[str, Any]:
    """
    Perform a login operation using a token. To get a token, you can use our own token generator tool, free to use:
    https://developers.layrz.com/tools/wialon-token-generator
    :param token: defines the token to use, must be a string

    :type token: str

    :return: the response from the server, must be a dict
    """
    result = self.token_login({'token': token})
    if not isinstance(result, dict):
      raise SdkException('Internal error: invalid response type')
    self._user_id = result['user']['id']
    self._session_id = result['eid']
    return result

  def logout(self: Self) -> dict[str, Any]:
    """
    Logout the Wialon session. This method will invalidate the current session and clear the `session_id` and
    `user_id` properties to ensure that the session is no longer valid.

    :return: the response from the server, must be a dict
    """
    result = self.core_logout()
    if not isinstance(result, dict):
      raise SdkException('Internal error: invalid response type')
    return result

  def reverse_geocoding(self: Self, latitude: float, longitude: float, flags: int = 1255211008) -> str:
    """
    Reverse geocoding method using the Wialon API.

    !Note: Your Wialon session will use the default geocoding service, that may be Google services or Wialon services.

    :param latitude: Latitude of the location to reverse geocode
    :param longitude: Longitude of the location to reverse geocode
    :param flags: Flags for the reverse geocoding request, default is 125521
    """

    coordinates = json.dumps({'lon': longitude, 'lat': latitude})

    url = f'https://geocode-maps.wialon.com/{self.host}/gis_geocode?'
    url += f'coords=[{coordinates}]&flags={flags}&uid={self.user_id}'

    log.debug('Reverse geocoding called: latitude %s - longitude %s - flags %s', latitude, longitude, flags)
    log.debug('Reverse geocoding url: %s', url)

    try:
      request = requests.post(url=url)
      response = request.json()
      return cast(str, response[0])
    except Exception as e:  # pylint: disable=W0706
      raise SdkException(message=f'Internal error: {e}') from e

  def __getattr__(self: Self, name: str) -> Callable[..., dict[str, Any] | list[Any]]:
    """Method missing handler"""

    def method(*args: dict[str, Any], **kwargs: dict[str, Any]) -> dict[str, Any] | list[Any]:
      """Handler"""
      arguments: dict[str, Any] = {}

      if len(args) > 0:
        arguments = args[0]

      if len(kwargs) > 0:
        arguments.update(kwargs)

      return self.call(method=name, args=arguments)

    return method


__all__ = ['WialonSdk', 'SdkException', 'WialonError']

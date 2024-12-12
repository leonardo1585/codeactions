from requests import request
import json


def Run(engine):
    if engine.params.get('base_url'):
        base_url = engine.params.get('base_url')
    else:
        engine.result.set(str('base_url is required'), status_code=400, content_type='json')
        return

    if engine.params.get('utm_source'):
        utm_source = engine.params.get('utm_source')
    else:
        engine.result.set(str('utm_source is required'), status_code=400, content_type='json')
        return

    if engine.params.get('vtex_app_key'):
        vtex_app_key = engine.params.get('vtex_app_key')
    else:
        engine.result.set(str('vtex_app_key is required'), status_code=400, content_type='json')
        return

    if engine.params.get('vtex_app_token'):
        vtex_app_token = engine.params.get('vtex_app_token')
    else:
        engine.result.set(str('vtex_app_token is required'), status_code=400, content_type='json')
        return

    if engine.params.get('start_date'):
        start_date = engine.params.get('start_date')
        end_date = engine.params.get('end_date')
        status_code, result = proccess_data(base_url=base_url, utm_source=utm_source, start_date=start_date,
                                            end_date=end_date,
                                            vtex_app_token=vtex_app_token, vtex_app_key=vtex_app_key)
    else:
        status_code, result = proccess_data(base_url=base_url, utm_source=utm_source, vtex_app_token=vtex_app_token,
                                            vtex_app_key=vtex_app_key)

    result = json.dumps(result)
    engine.result.set(result, status_code=status_code, content_type='json')


def vtex_utm(page_number: int, utm_source: str, start_date: None, end_date: None, vtex_app_token: str,
             vtex_app_key: str, base_url: str):
    if start_date is not None:
        url = f'https://{base_url}.myvtex.com/api/oms/pvt/orders/?f_UtmSource={utm_source}&per_page=100&page={page_number}&f_authorizedDate=authorizedDate:[{start_date} TO {end_date}]&f_status=invoiced'
    else:
        url = f'https://{base_url}.myvtex.com/api/oms/pvt/orders/?f_UtmSource={utm_source}&per_page=100&page={page_number}&f_status=invoiced'

    headers = {
        'X-Vtex-Api-Apptoken': vtex_app_token,
        'X-Vtex-Api-Appkey': vtex_app_key
    }

    result = request('GET', url=url, headers=headers)
    status_code = result.status_code
    result = result.json()

    return status_code, result


def proccess_data(base_url: str, utm_source: str, start_date: None = None, end_date: None = None, vtex_app_token=None,
                  vtex_app_key=None):
    total_value = 0
    total_vendas = 0
    max_value = float('-inf')
    min_value = float('inf')

    status_code, dados = vtex_utm(page_number=1, base_url=base_url, utm_source=utm_source, start_date=start_date,
                                  end_date=end_date, vtex_app_key=vtex_app_key, vtex_app_token=vtex_app_token)

    if 'list' not in dados or not dados['list']:
        return status_code, dados

    pages = dados['paging']['pages']

    for page in range(1, pages + 1):
        status_code, results = vtex_utm(page_number=page, utm_source=utm_source, base_url=base_url,
                                        start_date=start_date, end_date=end_date, vtex_app_token=vtex_app_token,
                                        vtex_app_key=vtex_app_key)
        for result in results['list']:
            if result['status'] != 'canceled':
                totalValue = result['totalValue']
                total_value += totalValue
                total_vendas += 1

                if totalValue > max_value:
                    max_value = totalValue
                if totalValue < min_value:
                    min_value = totalValue

    total_value /= 100
    max_value /= 100
    min_value /= 100

    return status_code, {
        'countSell': total_vendas,
        'accumulatedTotal': total_value,
        'ticketMax': max_value,
        'ticketMin': min_value
    }

# -*- coding: utf-8 -*-
import traceback
import re
import csv
import json
import time
import requests
from requests.exceptions import ProxyError, SSLError, ConnectTimeout
from uszipcode import ZipcodeSearchEngine
from lxml.html import fromstring

PROXY = '34.213.55.239:3128'


def get_states():
    states_map = {
        "AL": "Alabama",
        "AK": "Alaska",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DE": "Delaware",
        "DC": "District Of Columbia",
        "FL": "Florida",
        "GA": "Georgia",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "PR": "Puerto Rico",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VA": "Virginia",
        "VT": "Vermont",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming",
    }
    # states_map = {"IL": "Illinois"}
    # states_map = {"SC": "South Carolina"}
    return states_map


def run():
    url = "https://tools.silversneakers.com/Eligibility/HealthPlans"
    fieldnames = [
        'State', 'Company', 'Plans'
    ]
    states_map = get_states()
    state_index = 1
    with open(
      'silver_sneakers_plans_{}.csv'.format(int(time.time())), 'w', encoding='utf-8') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        for code, state in states_map.items():
            new_line = '\n'
            limiter = '-----------------------------------------'\
                      '-------------------------------------------'
            print(new_line, limiter)
            print(
                state_index,
                f"State: {state}",
                f"Code: {code}",
                new_line,
                limiter
            )
            params = {
                "state": code,
            }
            while True:
                print(f'Using PROXY: {PROXY}')
                try:
                    res = requests.get(
                        url,
                        params=params,
                        proxies={'https': PROXY, 'http': PROXY},
                        timeout=10
                    )
                    if not res.content:
                        break
                    html_response = fromstring(res.content)
                    companies = html_response.xpath('//div[@id="grid"]/div')
                    for company in companies:
                        final_plans = list()
                        name = company.xpath('a/img/@alt')[0]
                        plans = company.xpath('div//br')
                        final_plans = company.xpath('div/div/div/text()')
                        if not final_plans:
                            extracted_plans = list()
                            old_value = None
                            for p in plans:
                                new_value = p.xpath('preceding-sibling::text()')
                                if not old_value:
                                    extracted_plans.append(' '.join(new_value))
                                    old_value = new_value
                                else:
                                    new_value = [n for n in new_value if n not in old_value]
                                    extracted_plans.append(' '.join(new_value))
                                    old_value = p.xpath('preceding-sibling::text()')
                            final_plans = [p.strip() for p in extracted_plans if p.strip()]
                        # print(name)
                        # print(state)
                        # print(final_plans)
                        csv_writer.writerow({
                            'State': state,
                            'Company': name,
                            'Plans': f'1. {final_plans[0]}'
                        })
                        for i, plan in enumerate(final_plans[1:], 2):
                            csv_writer.writerow({
                                'Plans': f'{i}. {plan}'
                            })

                    state_index += 1
                    break

                except (ProxyError, SSLError, ConnectTimeout) as PE:
                    print("PROXY is dead. Retrying...")
                    continue
                except Exception as e:
                    traceback.print_exc()
                    continue


if __name__ == '__main__':
    run()

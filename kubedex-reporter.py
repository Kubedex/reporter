#!/usr/bin/env python

from __future__ import print_function
import requests
import multiprocessing

kubedex_domain = 'https://kubedex.com'
resources_url = kubedex_domain + '/wp-json/wp/v2/resources'

r = requests.get(resources_url)
total_pages = int(r.headers['X-WP-TotalPages'])
page_list = list(range(1, total_pages + 1))

helm_incubator_exclude_list = ['common', 'gcloud-endpoints']
helm_stable_exclude_list = ['gcloud-endpoints']

def get_wordpress(page_list):
    output = []
    for p in page_list:
        page_result = requests.get(resources_url + '?page=' + str(p)).json()
        for i in page_result:
            output.append(i['slug'])
    return output

def get_helm(directory):
    helm_repos = []
    charts = requests.get('https://api.github.com/repos/helm/charts/contents/' + directory).json()
    for c in charts:
        if c['type'] == 'dir':
            helm_repos.append(c['name'])
    return helm_repos


pool = multiprocessing.Pool(processes=total_pages)
pool_outputs = pool.map(get_wordpress, (page_list,))
pool.close()
wordpress_slugs = [item for sublist in pool_outputs for item in sublist]

helm_incubator = get_helm('incubator')
helm_stable = get_helm('stable')
all_helm = set(list(helm_incubator + helm_stable))

print("Incubating: ")
print(list(set(set(helm_incubator) - set(helm_incubator_exclude_list)) - set(wordpress_slugs)))

print("Stable: ")
print(list(set(set(helm_stable) - set(helm_stable_exclude_list)) - set(wordpress_slugs)))

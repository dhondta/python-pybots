# -*- coding: UTF-8 -*-
"""Bot client dedicated to Shodan API.

"""
import re
from six import string_types
from tinyscript.helpers.data.types.network import *

from ..core.protocols.http import JSONBot
from ..core.utils.api import *


__all__ = ["ShodanAPI"]

URL = "https://api.shodan.io"


class ShodanAPI(JSONBot, API):
    """
    ShodanAPI class for communicating with the API of Shodan.
    
    Reference: https://developer.shodan.io/api
    Note:      All API methods are rate-limited to 1 request/second.

    :param apikey: API key
    :param args:   JSONBot / API arguments
    :param kwargs: JSONBot keyword-arguments
    """
    API_PLANS = {
        'basic':      ("Freelancer API", True),
        'corp':       ("Corporate API", False),
        'dev':        ("Membership", True),
        'oss':        ("Free", True),
        'plus':       ("Small Business API", False),
        'stream-100': ("Enterprise", False),
    }
    
    def __init__(self, apikey, *args, **kwargs):
        self.__api_info = None
        self.public = True
        API.__init__(self, apikey, **kwargs)
        JSONBot.__init__(self, URL, *args, **kwargs)

    def __facet_str(self, *facets):
        """
        Converts a list of facets to a string, suitable for a request.
        
        :param facets: list of strings or pairs
        """
        r = []
        for f in facets:
            if isinstance(f, string_types):
                r.append(f)
            elif isinstance(f, tuple) and len(f) == 2:
                r.append("{}:{}".format(*f))
            else:
                raise ValueError("Bad facet")
        return ",".join(r)
    
    def __validate(**kwargs):
        """
        Private generic validation function for Shodan API arguments.
        """
        for k, v in kwargs.items():
            if k == "domain":
                domain_name(v)
            elif k in ["history", "minify", "notify"]:
                for f in v:
                    if not isinstance(f, bool):
                        raise ValueError("Bad boolean flag")
            elif k == "hostnames":
                for hn in v:
                    hostname(hn)
            elif k == "id" and not re.match(r"^[0-9A-Z]{16}$"):
                raise ValueError("Bad ID")
            elif k == "ips":
                for ip in v:
                    ip_address(ip)
            elif k == "order":
                if v not in ["asc", "desc"]:
                    raise ValueError("'order' must be one of: asc|desc")
            elif k in ["page", "size"]:
                positive_int(v, False)
            elif k == "port":
                port_number(v)
            elif k == "protocol":
                if v not in self.shodan.protocols().keys():
                    raise ValueError("Bad protocol")
            elif k == "sort":
                if v not in ["votes", "timestamp"]:
                    raise ValueError("'sort' must be one of: votes|timestamp")

    @time_throttle(1)
    def _get(self, method, reqpath, **kwargs):
        """
        Generic API sending method for appending the API key to the parameters.

        :param method:  HTTP method
        :param reqpath: request path
        """
        getattr(self, method)(reqpath + "?key=%s" % self._api_key, **kwargs)

    @apicall
    @cache(300)
    def account_profile(self):
        """
        Returns information about the Shodan account linked to this API key.
        """
        self._get("get", "/account/profile")
    
    @apicall
    @private
    @cache(300)
    def dns_domain(self, domain):
        """
        Get all the subdomains and other DNS entries for the given domain.
         Uses 1 query credit per lookup.
        """
        self.__validate(domain=domain)
        self._get("get", "/dns/domain/%s" % domain)

    @apicall
    @cache(300)
    def dns_resolve(self, *hostnames):
        """
        Look up the IP address for the provided list of hostnames.
        
        :param hostnames: comma-separated list of hostnames
        """
        self.__validate(hostnames=hostnames)
        r, params = {}, {'hostnames': ",".join(hostnames)}
        self._get("get", "/dns/resolve", params=params)

    @apicall
    @cache(300)
    def dns_reverse(self, *ips):
        """
        Look up the hostnames that have been defined for the given list of
         IP addresses.
        
        :param ips: comma-separated list of IP addresses
        """
        self.__validate(ips=ips)
        params = {'ips': ",".join(ips)}
        self._get("get", "/dns/reverse", params=params)
    
    @apicall
    @cache(300)
    def info(self):
        """
        Returns information about the API plan belonging to the given API key.
        """
        self._get("get", "/api-info")
        try:
            p, self.public = self.API_PLANS[self.json['plan']]
            self.logger.debug("API plan: {} ({})"
                             .format(p, ["private", "public"][self.public]))
        except:
            pass
    
    @apicall
    @cache(3600)
    def labs_honeyscore(self, ip):
        """
        Calculates a honeypot probability score ranging from 0 (not a honeypot)
         to 1.0 (is a honeypot).
        
        :param ip: host IP address
        """
        self.__validate(ips=[ip])
        self._get("get", "/labs/honeyscore/%s" % ip)
    
    @apicall
    @cache(300)
    def notifiers(self):
        """
        Get a list of all the notifiers that the user has created.
        """
        self._get("get", "/notifier")
    
    @apicall
    @cache(300)
    def notifier(self, id):
        """
        Get information about a notifier.
        
        :param id: notifier ID
        """
        self.__validate(id=id)
        self._get("get", "/notifier/%s" % id)
    
    @apicall
    @invalidate("notifiers")
    def notifier_delete(self, id):
        """
        Remove the notification service created for the user.
        
        :param id: notifier ID
        """
        self.__validate(id=id)
        self._get("delete", "/notifier/%s" % id)
    
    @apicall
    def notifier_edit(self, id, **data):
        """
        Update the parameters of a notifier.
        
        :param id: notifier ID
        """
        self.__validate(id=id)
        self._get("put", "/notifier", data=data)
    
    @apicall
    @invalidate("notifiers")
    def notifier_new(self, **data):
        """
        Create a new notification service endpoint that Shodan services can send
         notifications through.
        """
        self._get("post", "/notifier", data=data)
    
    @apicall
    @cache(86400)
    def notifier_provider(self):
        """
        Get a list of all the notification providers that are available and the
         parameters to submit when creating them.
        """
        self._get("get", "/notifier/provider")
    
    @apicall
    @private
    @cache(3600)
    def org(self):
        """
        Get information about your organization such as the list of its members,
         upgrades, authorized domains and more.
        """
        self._get("get", "/org")
    
    @apicall
    @private
    @cache(3600)
    def org_member_add(self, user, notify=False):
        """
        Add a Shodan user to the organization and upgrade them.
        """
        self.__validate(user=user, notify=notify)
        self._get("put", "/org/member/%s" % user, data={'notify': notify})
    
    @apicall
    @private
    @cache(3600)
    def org_member_delete(self, user):
        """
        Remove and downgrade the provided member from the organization.
        """
        self.__validate(user=user)
        self._get("delete", "/org/member/%s" % user)
    
    @apicall
    @cache(3600)
    def shodan_alerts(self):
        """
        Returns a listing of all the network alerts that are currently
         active on the account.
        """
        self._get("get", "/shodan/alert/info")
    
    @apicall
    @invalidate("shodan_alerts")
    def shodan_alert(self, id):
        """
        Returns the information about a specific network alert.
        
        :param id: alert ID that was returned by /shodan/alert
        """
        self.__validate(id=id)
        self._get("get", "/shodan/alert/%s/info" % id)
    
    @apicall
    @invalidate("shodan_alerts")
    def shodan_alert_delete(self, id):
        """
        Remove the specified network alert.
        
        :param id: alert ID
        """
        self.__validate(id=id)
        self._get("delete", "/shodan/alert/%s" % id)
    
    @apicall
    @cache(300)
    def shodan_alert_notifier(self, id, notifier_id):
        """
        Add the specified notifier to the network alert. Notifications are only
         sent if triggers have also been enabled.
        
        :param id:          alert ID
        :param notifier_id: notifier ID
        """
        self.__validate(ids=[id, notifier_id])
        self._get("get", "/shodan/alert/%s/notifier/%s" % (id, notifier_id))
    
    @apicall
    @invalidate("shodan_alert_notifier")
    def shodan_alert_notifier_delete(self, id, notifier_id):
        """
        Remove the notification service from the alert. Notifications are only
         sent if triggers have also been enabled.
        
        :param id:          alert ID
        :param notifier_id: notifier ID
        """
        self.__validate(ids=[id, notifier_id])
        self._get("delete", "/shodan/alert/%s/notifier/%s" % (id, notifier_id))
    
    @apicall
    @cache(3600)
    def shodan_alert_triggers(self):
        """
        Returns a listing of all the network alerts that are currently
         active on the account.
        """
        self._get("get", "/shodan/alert/triggers")
    
    @apicall
    @cache(300)
    def shodan_alert_trigger(self, id, trigger):
        """
        Get notifications when the specified trigger is met.
        
        :param id:      alert ID
        :param trigger: trigger name
        """
        self.__validate(id=id, trigger=trigger)
        self._get("get", "/shodan/alert/%s/trigger/%s" % (id, trigger))
    
    @apicall
    @invalidate("shodan_alert_triggers", "shodan_alert_trigger")
    @cache(300)
    def shodan_alert_trigger_delete(self, id, trigger):
        """
        Stop getting notifications for the specified trigger.
        
        :param id:      alert ID
        :param trigger: trigger name
        """
        self.__validate(id=id, trigger=trigger)
        self._get("delete", "/shodan/alert/%s/trigger/%s" % (id, trigger))
    
    @apicall
    @cache(300)
    def shodan_alert_trigger_ignore(self, id, trigger, service):
        """
        Ignore the specified service when it is matched for the trigger.
        
        :param id:      alert ID
        :param trigger: trigger name
        :param service: service specified in the format "ip:port"
        """
        self.__validate(id=id, service=service, trigger=trigger)
        self._get("put", "/shodan/alert/%s/trigger/%s/ignore/%s" % \
                  (id, trigger, service))
    
    @apicall
    @invalidate("shodan_alert_trigger_ignore")
    @cache(300)
    def shodan_alert_trigger_ignore_delete(self, id, trigger, service):
        """
        Start getting notifications again for the specified trigger.
        
        :param id:      alert ID
        :param trigger: trigger name
        :param service: service specified in the format "ip:port"
        """
        self.__validate(id=id, service=service, trigger=trigger)
        self._get("delete", "/shodan/alert/%s/trigger/%s/ignore/%s" % \
                  (id, trigger, service))
    
    @apicall
    @private
    @cache(3600)
    def shodan_datasets(self):
        """
        See a list of the datasets that are available for download.
        """
        self._get("get", "/shodan/data")
    
    @apicall
    @private
    @cache(300)
    def shodan_dataset(self, dataset):
        """
        Get a list of files that are available for download from the provided
         dataset.
        
        :param dataset: name of the dataset
        """
        self.__validate(dataset=dataset)
        params = {'dataset': dataset}
        self._get("get", "/shodan/data", params=params)
    
    @apicall
    @cache(3600)
    def shodan_host(self, ip, history=False, minify=False):
        """
        Returns all services that have been found on the given host IP.
        
        :param ip:      host IP address
        :param history: True if all historical banners should be returned
        :param minify:  True to only return the list of ports and the
                         general host information, no banners
        """
        self.__validate(ips=[ip], history=history, minify=minify])
        params = {'history': history, 'minify': minify}
        self._get("get", "/shodan/host/%s" % ip, params=params)
    
    @apicall
    @cache(3600)
    def shodan_host_count(self, query, *facets):
        """
        This method behaves identical to "/shodan/host/search" with the only
         difference that this method does not return any host results, it only
         returns the total number of results that matched the query and any
         facet information that was requested. As a result this method does not
         consume query credits.

        :param query:  Shodan search query
        :param facets: comma-separated list of properties to get summary
                        information on
        """
        facets = self.__facet_str(facets)
        self.__validate(query=query, facets=facets)
        params = {}
        if facets != "":
            params['facets'] = facets
        self._get("get", "/shodan/host/count", params=params)
    
    def shodan_host_search(self, query, *facets, **kwargs):
        """
        Search Shodan using the same query syntax as the website and use facets
         to get summary information for different properties. This method may
         use API query credits depending on usage.

        :param query:  Shodan search query
        :param facets: comma-separated list of properties to get summary
                        information on
        :param page:   page number to page through results 100 at a time
        :param minify: whether or not to truncate larger fields
        """
        page = kwargs.get('page', 1)
        minify = kwargs.get('minify', False)
        facets = self.__facet_str(facets)
        self.__validate(query=query, facets=facets, page=page, flags=[minify])
        params = {'query': query, 'page': page, 'minify': minify}
        if facets != "":
            params['facets'] = facets
        self._get("get", "/shodan/host/search", params=params)
    
    @property
    @cache(86400)
    def shodan_host_search_facets(self):
        """
        Returns a list of facets that can be used to get a breakdown of the top
         values for a property.
        """
        self._get("get", "/shodan/host/search/facets")
    
    @property
    @cache(86400)
    def shodan_host_search_filters(self):
        """
        Returns a list of facets that can be used to get a breakdown of the top
         values for a property.
        """
        self._get("get", "/shodan/host/search/filters")
    
    def shodan_host_search_tokens(self, query):
        """
        Lets the user determine which filters are being used by the query string
         and what parameters were provided to the filters.

        :param query:  Shodan search query
        """
        self.__validate(query=query)
        params = {'query': query}
        self._get("get", "/shodan/host/search/tokens", params=params)
    
    @apicall
    @cache(86400)
    def shodan_ports(self):
        """
        Returns a list of port numbers that the crawlers are looking for.
        """
        self._get("get", "/shodan/ports")
    
    @apicall
    @cache(86400)
    def shodan_protocols(self):
        """
        Returns an object containing all the protocols that can be used when
         launching an Internet scan.
        """
        self._get("get", "/shodan/protocols")
    
    @apicall
    @cache(300)
    def shodan_query(self, page=0, sort="votes", order="asc"):
        """
        Obtain a list of search queries that users have saved in Shodan.
        
        :param page:  page number to iterate over results; each page contains 10
                       items 
        :param sort:  sort the list based on a property (votes|timestamp)
        :param order: whether to sort the list in ascending or descending order
                       (asc|desc)
        """
        self.__validate(page=page, order=order, sort=sort)
        params = {'page': page, 'sort': sort, 'order': order}
        self._get("get", "/shodan/query", params=params)
    
    @apicall
    @cache(300)
    def shodan_query_search(self, query, page=0):
        """
        Search the directory of search queries that users have saved in Shodan.
        
        :param query: what to search for in the directory of saved search
                       queries
        :param page:  page number to iterate over results; each page contains 10
                       items 
        """
        self.__validate(query=query, page=page)
        params = {'query': query, 'page': page}
        self._get("get", "/shodan/query/search", params=params)
    
    @apicall
    @cache(3600)
    def shodan_query_tags(self, size=10):
        """
        Obtain a list of popular tags for the saved search queries in Shodan.
        
        :param size: number of tags to return
        """
        self.__validate(size=size)
        params = {'size': size}
        self._get("get", "/shodan/query/tags", params=params)
    
    @apicall
    def shodan_scan(self, id):
        """
        Check the progress of a previously submitted scan request.
        
        Possible status: SUBMITTING|QUEUE|PROCESSING|DONE
        
        :param id: unique scan ID that was returned by /shodan/scan
        """
        self.__validate(id=id)
        self._get("get", "/shodan/scan/%s" % id)
    
    @apicall
    @cache(3600)
    def shodan_scan_internet(self, port, protocol):
        """
        Request Shodan to crawl the Internet for a specific port.
        
        NB: This method is restricted to security researchers and companies with
             a Shodan Enterprise Data license. To apply for access to this
             method as a researcher, please email jmath@shodan.io with
             information about your project. Access is restricted to prevent
             abuse.
        
        :param port:     port that Shodan should crawl the Internet for
        :param protocol: name of the protocol that should be used to interrogate
                          the port (see /shodan/protocols for a list of
                          supported protocols)
        """
        self.__validate(port=port, protocol=protocol)
        data = {'port': port, 'protocol': protocol}
        self._get("post", "/shodan/scan/internet", data=data)
    
    @apicall
    def shodan_scan_new(self, *ips):
        """
        Request Shodan to crawl a network.
        
        NB: This method uses API scan credits: 1 IP consumes 1 scan credit. You
             must have a paid API plan (either one-time payment or subscription)
             in order to use this method.
        
        :param ips: comma-separated list of IPs or netblocks (in CIDR notation)
                     that should get crawled
        """
        self.__validate(ips=ips)
        data = {'ips': ",".join(ips)}
        self._get("post", "/shodan/scan", data=data)
    
    @apicall
    @cache(300)
    def tools_httpheaders(self):
        """
        Shows the HTTP headers that your client sends when connecting to a
         webserver.
        """
        self._get("get", "/tools/httpheaders")
    
    @apicall
    @cache(300)
    def tools_myip(self):
        """
        Get your current IP address as seen from the Internet.
        """
        self._get("get", "/tools/myip")

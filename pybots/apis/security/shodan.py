# -*- coding: UTF-8 -*-
"""API client dedicated to Shodan.

"""
import re
from six import string_types
from tinyscript.helpers.data.types.common import positive_int
from tinyscript.helpers.data.types.network import *

from ...core.utils.api import *


__all__ = ["ShodanAPI", "ShodanExploitsAPI"]


class BaseAPI(API):
    """
    Base class for communicating with the API of Shodan.

    Note:      All API methods are rate-limited to 1 request/second.
    """
    def _facet_str(self, *facets):
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

    @time_throttle(1)
    def _request(self, method, reqpath, **kwargs):
        """
        Generic API sending method for appending the API key to the parameters.

        :param method:  HTTP method
        :param reqpath: request path
        """
        reqpath += "?key=%s" % self._api_key
        super(BaseAPI, self)._request(reqpath, method, **kwargs)

    def _validate(self, **kwargs):
        """
        Private generic validation function for API arguments.
        """
        # FIXME: validate 'query'
        for k, v in kwargs.items():
            if k == "asn":
                for asn in v.split(","):
                    as_number(asn)
            elif k == "domain":
                domain_name(v)
            elif k == "filters":
                if not isinstance(v, dict) and list(v.keys()) == ["ip"]:
                    raise ValueError("bad filters dictionary")
            elif k in ["history", "minify", "notify"]:
                if not isinstance(v, bool):
                    raise ValueError("bad boolean flag")
            elif k == "hostnames":
                for hn in v:
                    hostname(hn)
            elif k == "id" and not re.match(r"^[0-9A-Z]{16}$"):
                raise ValueError("bad ID format, should be: [0-9A-Z]{16}")
            elif k == "ips":
                for ip in v:
                    ip_address(ip)
            elif k == "order":
                if v not in ["asc", "desc"]:
                    raise ValueError("'order' must be one of: asc|desc")
            elif k in ["page", "size"]:
                positive_int(v, True)
            elif k == "port":
                port_number(v)
            elif k == "protocol":
                if v not in self.shodan.protocols().keys():
                    raise ValueError("bad protocol, check .protocols() to get the list of valid ones")
            elif k == "sort":
                if v not in ["votes", "timestamp"]:
                    raise ValueError("'sort' must be one of: votes|timestamp")


class ShodanAPI(BaseAPI):
    """
    Class for communicating with the API of Shodan.
    
    Reference: https://developer.shodan.io/api

    :param apikey: API key
    :param args:   JSONBot / API arguments
    :param kwargs: JSONBot keyword-arguments
    """
    plans = {
        'basic':      ("Freelancer API", True),
        'corp':       ("Corporate API", False),
        'dev':        ("Membership", True),
        'oss':        ("Free", True),
        'plus':       ("Small Business API", False),
        'stream-100': ("Enterprise", False),
    }
    url = "https://api.shodan.io"
    
    def __init__(self, apikey, *args, **kwargs):
        self.public = True
        super(ShodanAPI, self).__init__(apikey, *args, **kwargs)

    @apicall
    @cache(3600)
    def account_profile(self):
        """
        Returns information about the Shodan account linked to this API key.
        """
        self._request("get", "/account/profile")
    
    @apicall
    @private
    @invalidate("account_profile", "info")
    @cache(300)
    def dns_domain(self, domain):
        """
        Get all the subdomains and other DNS entries for the given domain. Uses 1 query credit per lookup.
        """
        self._validate(domain=domain)
        self._request("get", "/dns/domain/%s" % domain)

    @apicall
    @cache(300, 3)
    def dns_resolve(self, *hostnames):
        """
        Look up the IP address for the provided list of hostnames.
        
        :param hostnames: comma-separated list of hostnames
        """
        self._validate(hostnames=hostnames)
        self._request("get", "/dns/resolve", params={'hostnames': ",".join(hostnames)})

    @apicall
    @cache(300, 3)
    def dns_reverse(self, *ips):
        """
        Look up the hostnames that have been defined for the given list of IP addresses.
        
        :param ips: comma-separated list of IP addresses
        """
        self._validate(ips=ips)
        self._request("get", "/dns/reverse", params={'ips': ",".join(ips)})

    @apicall
    @cache(300)
    def info(self):
        """
        Returns information about the API plan belonging to the given API key.
        """
        self._request("get", "/api-info")
        try:
            p, self.public = self.plans[self._json['plan']]
            self._disable_time_throttling = not self.public
            self._logger.debug("API plan: {} ({})".format(p, ["private", "public"][self.public]))
        except:
            pass
    
    @apicall
    @cache(3600)
    def labs_honeyscore(self, ip):
        """
        Calculates a honeypot probability score ranging from 0 (not a honeypot) to 1.0 (is a honeypot).
        
        :param ip: host IP address
        """
        self._validate(ips=[ip])
        self._request("get", "/labs/honeyscore/%s" % ip)
    
    @apicall
    @cache(300)
    def notifiers(self):
        """
        Get a list of all the notifiers that the user has created.
        """
        self._request("get", "/notifier")
    
    @apicall
    @cache(300)
    def notifier(self, id):
        """
        Get information about a notifier.
        
        :param id: notifier ID
        """
        self._validate(id=id)
        self._request("get", "/notifier/%s" % id)
    
    @apicall
    @invalidate("notifiers")
    def notifier_delete(self, id):
        """
        Remove the notification service created for the user.
        
        :param id: notifier ID
        """
        self._validate(id=id)
        self._request("delete", "/notifier/%s" % id)
    
    @apicall
    def notifier_edit(self, id, **data):
        """
        Update the parameters of a notifier.
        
        :param id: notifier ID
        """
        self._validate(id=id)
        self._request("put", "/notifier", data=data)
    
    @apicall
    @invalidate("notifiers")
    def notifier_new(self, **data):
        """
        Create a new notification service endpoint that Shodan services can send notifications through.
        """
        self._request("post", "/notifier", data=data)
    
    @apicall
    @cache(86400)
    def notifier_provider(self):
        """
        Get a list of all the notification providers that are available and the parameters to submit when creating them.
        """
        self._request("get", "/notifier/provider")
    
    @apicall
    @private
    @cache(3600)
    def org(self):
        """
        Get information about your organization such as the list of its members, upgrades, authorized domains and more.
        """
        self._request("get", "/org")
    
    @apicall
    @private
    @invalidate("org")
    @cache(3600)
    def org_member_add(self, user, notify=False):
        """
        Add a Shodan user to the organization and upgrade them.
        """
        self._validate(user=user, notify=notify)
        self._request("put", "/org/member/%s" % user, data={'notify': notify})
    
    @apicall
    @private
    @invalidate("org")
    @cache(3600)
    def org_member_delete(self, user):
        """
        Remove and downgrade the provided member from the organization.
        """
        self._validate(user=user)
        self._request("delete", "/org/member/%s" % user)
    
    @apicall
    @cache(3600)
    def shodan_alerts(self):
        """
        Returns a listing of all the network alerts that are currently active on the account.
        """
        self._request("get", "/shodan/alert/info")
    
    @apicall
    def shodan_alert(self, id):
        """
        Returns the information about a specific network alert.
        
        :param id: alert ID that was returned by /shodan/alert
        """
        self._validate(id=id)
        self._request("get", "/shodan/alert/%s/info" % id)
    
    @apicall
    @invalidate("notifiers")
    def shodan_alert_new(self, name, filters=None, expires=0):
        """
        Create a network alert for a defined IP/ netblock which can be used to subscribe to changes/ events that are
         discovered within that range.
        
        :param name:    name to describe the network alert
        :param filters: object specifying the criteria that an alert should trigger
                        NB: The only supported option at the moment is the "ip" filter.
        :param expires: number of seconds that the alert should be active
        """
        self._validate(filters=filters)
        data = {'name': name, 'filters': filters}
        if expires > 0:
            data['expires'] = expires
        self._request("post", "/shodan/alert", data=data)
    
    @apicall
    @invalidate("shodan_alerts")
    def shodan_alert_delete(self, id):
        """
        Remove the specified network alert.
        
        :param id: alert ID
        """
        self._validate(id=id)
        self._request("delete", "/shodan/alert/%s" % id)
    
    @apicall
    @cache(300)
    def shodan_alert_notifier(self, id, notifier_id):
        """
        Add the specified notifier to the network alert. Notifications are only sent if triggers have also been enabled.
        
        :param id:          alert ID
        :param notifier_id: notifier ID
        """
        self._validate(ids=[id, notifier_id])
        self._request("get", "/shodan/alert/%s/notifier/%s" % (id, notifier_id))
    
    @apicall
    @invalidate("shodan_alert_notifier")
    def shodan_alert_notifier_delete(self, id, notifier_id):
        """
        Remove the notification service from the alert. Notifications are only sent if triggers have also been enabled.
        
        :param id:          alert ID
        :param notifier_id: notifier ID
        """
        self._validate(ids=[id, notifier_id])
        self._request("delete", "/shodan/alert/%s/notifier/%s" % (id, notifier_id))
    
    @apicall
    @cache(3600)
    def shodan_alert_triggers(self):
        """
        Returns a listing of all the network alerts that are currently active on the account.
        """
        self._request("get", "/shodan/alert/triggers")
    
    @apicall
    @cache(300)
    def shodan_alert_trigger(self, id, trigger):
        """
        Get notifications when the specified trigger is met.
        
        :param id:      alert ID
        :param trigger: trigger name
        """
        self._validate(id=id, trigger=trigger)
        self._request("get", "/shodan/alert/%s/trigger/%s" % (id, trigger))
    
    @apicall
    @invalidate("shodan_alert_triggers", "shodan_alert_trigger")
    @cache(300)
    def shodan_alert_trigger_delete(self, id, trigger):
        """
        Stop getting notifications for the specified trigger.
        
        :param id:      alert ID
        :param trigger: trigger name
        """
        self._validate(id=id, trigger=trigger)
        self._request("delete", "/shodan/alert/%s/trigger/%s" % (id, trigger))
    
    @apicall
    @cache(300)
    def shodan_alert_trigger_ignore(self, id, trigger, service):
        """
        Ignore the specified service when it is matched for the trigger.
        
        :param id:      alert ID
        :param trigger: trigger name
        :param service: service specified in the format "ip:port"
        """
        self._validate(id=id, service=service, trigger=trigger)
        self._request("put", "/shodan/alert/%s/trigger/%s/ignore/%s" % (id, trigger, service))
    
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
        self._validate(id=id, service=service, trigger=trigger)
        self._request("delete", "/shodan/alert/%s/trigger/%s/ignore/%s" % (id, trigger, service))
    
    @apicall
    @private
    @cache(3600)
    def shodan_datasets(self):
        """
        See a list of the datasets that are available for download.
        """
        self._request("get", "/shodan/data")
    
    @apicall
    @private
    @cache(300)
    def shodan_dataset(self, dataset):
        """
        Get a list of files that are available for download from the provided dataset.
        
        :param dataset: name of the dataset
        """
        self._validate(dataset=dataset)
        self._request("get", "/shodan/data", params={'dataset': dataset})
    
    @apicall
    @cache(3600)
    def shodan_host(self, ip, history=False, minify=False):
        """
        Returns all services that have been found on the given host IP.
        
        :param ip:      host IP address
        :param history: True if all historical banners should be returned
        :param minify:  True to only return the list of ports and the general host information, no banners
        """
        self._validate(ips=[ip], history=history, minify=minify)
        self._request("get", "/shodan/host/%s" % ip, params={'history': history, 'minify': minify})
    
    @apicall
    @cache(300)
    def shodan_host_count(self, query, *facets):
        """
        This method behaves identical to "/shodan/host/search" with the only difference that this method does not return
         any host results, it only returns the total number of results that matched the query and any facet information
         that was requested. As a result this method does not consume query credits.

        :param query:  Shodan search query
        :param facets: comma-separated list of properties to get summary information on
        """
        facets = self._facet_str(*facets)
        self._validate(query=query, facets=facets)
        params = {'query': query}
        if facets != "":
            params['facets'] = facets
        self._request("get", "/shodan/host/count", params=params)
    
    @apicall
    @invalidate("account_profile", "info")
    @cache(300)
    def shodan_host_search(self, query, *facets, **kwargs):
        """
        Search Shodan using the same query syntax as the website and use facets to get summary information for different
         properties. This method may use API query credits depending on usage.

        :param query:  Shodan search query
        :param facets: comma-separated list of properties to get summary information on
        :param page:   page number to page through results 100 at a time
        :param minify: whether or not to truncate larger fields
        """
        self._validate(query=query)
        params = {'query': query}
        if self.public:
            if kwargs.get('page') or kwargs.get('minify') or facets:
                raise APIError("Please upgrade your API plan to use filters or paging.")
        else:
            page = kwargs.get('page', 1)
            minify = kwargs.get('minify', False)
            facets = self._facet_str(*facets)
            self._validate(facets=facets, page=page, minify=minify)
            params = {'page': page, 'minify': minify}
            if facets != "":
                params['facets'] = facets
        self._request("get", "/shodan/host/search", params=params)
    
    @apicall
    @cache(86400)
    def shodan_host_search_facets(self):
        """
        Returns a list of facets that can be used to get a breakdown of the top values for a property.
        """
        self._request("get", "/shodan/host/search/facets")
    
    @apicall
    @cache(86400)
    def shodan_host_search_filters(self):
        """
        Returns a list of facets that can be used to get a breakdown of the top values for a property.
        """
        self._request("get", "/shodan/host/search/filters")
    
    @apicall
    def shodan_host_search_tokens(self, query):
        """
        Lets the user determine which filters are being used by the query string and what parameters were provided to
         the filters.

        :param query: Shodan search query
        """
        self._validate(query=query)
        self._request("get", "/shodan/host/search/tokens", params={'query': query})
    
    @apicall
    @cache(86400)
    def shodan_ports(self):
        """
        Returns a list of port numbers that the crawlers are looking for.
        """
        self._request("get", "/shodan/ports")
    
    @apicall
    @cache(86400)
    def shodan_protocols(self):
        """
        Returns an object containing all the protocols that can be used when launching an Internet scan.
        """
        self._request("get", "/shodan/protocols")
    
    @apicall
    @cache(300)
    def shodan_query(self, page=0, sort="votes", order="asc"):
        """
        Obtain a list of search queries that users have saved in Shodan.
        
        :param page:  page number to iterate over results; each page contains 10 items
        :param sort:  sort the list based on a property (votes|timestamp)
        :param order: whether to sort the list in ascending or descending order (asc|desc)
        """
        self._validate(page=page, order=order, sort=sort)
        self._request("get", "/shodan/query", params={'page': page, 'sort': sort, 'order': order})
    
    @apicall
    @cache(300)
    def shodan_query_search(self, query, page=0):
        """
        Search the directory of search queries that users have saved in Shodan.
        
        :param query: what to search for in the directory of saved search queries
        :param page:  page number to iterate over results; each page contains 10 items
        """
        self._validate(query=query, page=page)
        self._request("get", "/shodan/query/search", params={'query': query, 'page': page})
    
    @apicall
    @cache(3600)
    def shodan_query_tags(self, size=10):
        """
        Obtain a list of popular tags for the saved search queries in Shodan.
        
        :param size: number of tags to return
        """
        self._validate(size=size)
        self._request("get", "/shodan/query/tags", params={'size': size})
    
    @apicall
    def shodan_scan(self, id):
        """
        Check the progress of a previously submitted scan request.
        
        Possible status: SUBMITTING|QUEUE|PROCESSING|DONE
        
        :param id: unique scan ID that was returned by /shodan/scan
        """
        self._validate(id=id)
        self._request("get", "/shodan/scan/%s" % id)
    
    @apicall
    @cache(3600)
    def shodan_scan_internet(self, port, protocol):
        """
        Request Shodan to crawl the Internet for a specific port.
        
        NB: This method is restricted to security researchers and companies with a Shodan Enterprise Data license. To
             apply for access to this method as a researcher, please email jmath@shodan.io with information about your
             project. Access is restricted to prevent abuse.
        
        :param port:     port that Shodan should crawl the Internet for
        :param protocol: name of the protocol that should be used to interrogate the port (see /shodan/protocols for a
                          list of supported protocols)
        """
        self._validate(port=port, protocol=protocol)
        self._request("post", "/shodan/scan/internet", data={'port': port, 'protocol': protocol})
    
    @apicall
    @private
    @invalidate("account_profile", "info")
    def shodan_scan_new(self, *ips):
        """
        Request Shodan to crawl a network.
        
        NB: This method uses API scan credits: 1 IP consumes 1 scan credit. You must have a paid API plan (either
             one-time payment or subscription) in order to use this method.
        
        :param ips: comma-separated list of IPs or netblocks (in CIDR notation) that should get crawled
        """
        self._validate(ips=ips)
        self._request("post", "/shodan/scan", data={'ips': ",".join(ips)})
    
    @apicall
    @cache(300)
    def tools_httpheaders(self):
        """
        Shows the HTTP headers that your client sends when connecting to a webserver.
        """
        self._request("get", "/tools/httpheaders")
    
    @apicall
    @cache(300)
    def tools_myip(self):
        """
        Get your current IP address as seen from the Internet.
        """
        self._request("get", "/tools/myip")


class ShodanExploitsAPI(BaseAPI):
    """
    Class for communicating with the API of ShodanExploits.

    Reference: https://developer.shodan.io/api/exploits/rest

    :param apikey: API key
    :param args:   JSONBot / API arguments
    :param kwargs: JSONBot keyword-arguments
    """
    url = "https://exploits.shodan.io/api"

    @apicall
    @cache(300)
    def exploits_count(self, query, *facets):
        """
        Count exploits from a variety of data sources.

        :param query:  Shodan search query
        :param facets: comma-separated list of properties to get summary information on
        """
        facets = self._facet_str(*facets)
        self._validate(query=query, facets=facets)
        params = {'query': query}
        if facets != "":
            params['facets'] = facets
        self._request("get", "/count", params=params)

    @apicall
    @cache(3600)
    def exploits_search(self, query, *facets, **kwargs):
        """
        Search across a variety of data sources for exploits and use facets to get summary information.

        :param query:  Shodan search query
        :param facets: comma-separated list of properties to get summary information on
        :param page:   page number to page through results 100 at a time
        """
        page = kwargs.get('page', 1)
        facets = self._facet_str(*facets)
        self._validate(query=query, facets=facets, page=page)
        params = {'query': query, 'page': page}
        if facets != "":
            params['facets'] = facets
        self._request("get", "/search", params=params)


class ShodanStreamAPI(BaseAPI):
    """
    Class for communicating with the API of ShodanStream.

    Reference: https://developer.shodan.io/api/exploits/rest

    :param apikey: API key
    :param args:   JSONBot / API arguments
    :param kwargs: JSONBot keyword-arguments
    """
    url = "https://stream.shodan.io"

    @private
    def shodan_banners(self):
        for line in self._request("get", "/shodan/banners", stream=True):
            yield line


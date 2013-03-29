django-mobile-site-redirect-middleware
======================================

django middlewares,include SubdomainMiddleware,MobileRedirectMiddleware

包括2个middleware

- **SubdomainMiddleware**；让一个django project同时支持多个域名

- **MobileRedirectMiddleware** 根据用户user agent区分移动互联网用户，并重定向到移动网站

##如何把middleware添加到django 工程当中

- 下载代码 	
	cd ${you project}

	git clone https://github.com/lutaf/django-mobile-site-redirect-middleware

- 修改settings.py，在MIDDLEWARE_CLASSES 中添加 `'{YOU-PROJECT-NAME}.lutaf.middleware.SubdomainURLRoutingMiddleware',`,必须添加在`django.middleware.common.CommonMiddleware`之后


##SubdomainMiddleware使用方法

- 修改settings.py,加入url配置项

	SUBDOMAIN\_URLCONFS = {
  		None: 'lutaf.urls\_r',  # no subdomain, e.g. ``example.com``
    	'm': 'lutaf.urls\_m',
		#....
	}
	SUBDOMAIN_URLCONFS可以加入任意多项配置，如果没有匹配上，url请求会按照ROOT_URLCONF自定的url文件进行路由

- 更多文档:<http://django-subdomains.readthedocs.org>，SubdomainMiddleware不依赖任何db.Model


##MobileRedirectMiddleware使用方法

- 修改settings.py,加入url配置项

	SITE_INFO= {
	    'domain':'lutaf.com',
	    'mobile\_host':'m.lutaf.com',
	}

	注意： domain 是指域名本身，不是主站使用的host，如果主站启用www,也可以正常使用

- 移动浏览器 user agent 列表如下，可以随意修改

	DEFAULT\_UA\_STRINGS = (
	    'Android',
	    'BlackBerry',
	    'IEMobile',
	    'Maemo',
	    'Opera Mini',
	    'SymbianOS',
	    'WebOS',
	    'Windows Phone',
	    'iPhone',
	    'iPod',
	)
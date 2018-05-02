get search data
---------------

    curl 'https://fp.trafikverket.se/Boka/search-information' -H 'Cookie: FpsExternalIdentity=D172107651FFE95C52C67CB04A5523EEBC30C237551F12DAC03FDDF4ADA439547F1A8DC4E947DE31DE484DDDB88105D2D414785C9031AE6C58016A97A1372AC7A0029E5C5AF4CB67236BF48A0D441DE473FD252AE66B318906DF0642EB55FBAD6E1CD6B03D6FC6CA471D29503D2690D3DC7BF8CBCE7EFC1E74F5C4CC28C9800C27CEEABFC1693E4E5B47B90715393FEE; FORARPROV-FPS-WEB-EXT=ffffffff0914195e45525d5f4f58455e445a4a423660; _ga=GA1.2.827753902.1505159041; _gid=GA1.2.924853720.1525192324' -H 'Origin: https://fp.trafikverket.se' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en,en-US;q=0.9,zh-CN;q=0.8,zh;q=0.7,sv;q=0.6' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36' -H 'Content-Type: application/json' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: https://fp.trafikverket.se/Boka/' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --data-binary '{"bookingSession":{"socialSecurityNumber":"198670911-0000","licenceId":"5","bookingModeId":0,"ignoreDebt":false,"examinationTypeId":0,"rescheduleTypeId":"0"}}' --compressed


search with location id
-----------------------

    curl 'https://fp.trafikverket.se/Boka/occasion-bundles' -H 'Cookie: FpsExternalIdentity=5E9B30DC76D67400DC3C3186FC26E49C941CBA2865BD32DF8162E789CF418CD6194BB20A242628AD35EFC018758D43B8630BD4EE126056C18B002DF191ED5743E6C20F9627E00E18A35DC7EAB343746DC0746D6FFE2549BD441F289B7363012C70722E68009063A2B2E0E31F0F1B02FC6BFA398F2F70EEF578EE8331BB2097CE39168FBC3C5C6AB2B9978508F5DF2F47; _ga=GA1.2.827753902.1505159041; _gid=GA1.2.1445140.1505551432' -H 'Origin: https://fp.trafikverket.se' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.8' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36' -H 'Content-Type: application/json' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: https://fp.trafikverket.se/Boka/' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --data-binary '{"bookingSession":{"socialSecurityNumber":"19876543-1234","licenceId":5,"bookingModeId":0,"ignoreDebt":false,"examinationTypeId":12},"occasionBundleQuery":{"startDate":"2017-11-30T22:00:00.000Z","locationId":1000134,"languageId":4,"vehicleTypeId":2,"tachographTypeId":1,"occasionChoiceId":1,"examinationTypeId":0}}' --compressed
"""
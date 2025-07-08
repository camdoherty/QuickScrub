**IP Address (v4)**
IPv4: 192.168.1.101
IPv4: 10.0.0.25
IPv4: 172.16.254.1
IPv4: 8.8.8.8
IPv4: 203.0.113.42           # TEST-NET-3 (Documentation)
IPv4: 255.255.255.255        # Broadcast
IPv4: 223.255.255.255       # Last Class C address
IPv4: 100.64.0.1             # Shared Address Space

**Email**
Email: "weird.o'malley"@subdomain.example.museum
Email: first_last@localhost
Email: üser@exämple.org               # Unicode user and domain
Leading dot (invalid, but sometimes accepted)
Email: long.email.address.with.many.parts@very-long-domain-name-example.com
Email: mixedCase123.EMAIL@DoMaIn.CoM
Email: user@[IPv6:2001:db8::1]        # Email literal IPv6 domain
Email: user-123@sub.domain.co.uk
Email: "Display Name" <weird+filter.address@something-mail.ca>
Email: foo@[192.168.1.50]   # Literal IPv4 address
Email: alice.o’connor@unusual-domain.travel

**Phone Number**
Phone: +49 30 123456        # German, local short
Phone: 1800-FLOWERS         # US toll-free vanity
Phone: +81-3-1234-5678      # Japan, Tokyo
Phone: 09123 456789         # UK mobile
Phone: (02) 1234 5678       # Australia, landline, no country code
Phone: +33 1 23 45 67 89    # France
Phone: +7 495 123-45-67     # Russia, Moscow
Phone: (03)-1234-5678       # Japan, alternate national
Phone: 415-555-2671
Phone: 1-800-ALPHANUM  # Vanity
Phone: 020 7946 0958   # UK National
Phone: +91-9876543210  #

**Credit Card**
Credit Card (Visa): 4929 1234 5678 9012
Credit Card (Mastercard): 2221-0000-1234-5678    # New Mastercard range
Credit Card (Test, all 0s): 0000 0000 0000 0000  # Technically valid format
Credit Card (Spaces): 4111    1111   1111   1111
Credit Card (Short): 1234-5678-9012              # Short, invalid length (edge)

**MAC Address**
MAC: AA:BB:CC:DD:EE:FF
MAC: 01-23-45-67-89-ab
MAC: aa:bb:cc:dd:ee:ff
MAC: 0a:1b:2c:3d:4e:5f
MAC: 001122334455           # No separator (edge, sometimes valid for import)
MAC: FF:FF:FF:FF:FF:FF      # Broadcast MAC


**IP Address (v6)**
IPv6: 2001:db8:0:0:8d3:0:0:0     # Leading zeros omitted in segments
IPv6: 0:0:0:0:0:ffff:192.0.2.128 # IPv4-mapped IPv6
IPv6: ::ffff:192.0.2.128         # Compressed IPv4-mapped
IPv6: 2001:db8:1234:0000:0000:0000:0000:0001
IPv6: 2001:db8:1234::1           # Compressed edge
IPv6: ::                         # Unspecified address
IPv6: 2001:db8::abcd:ef12:3456:789a
IPv6: fe80::1%lo0                # Link-local with zone index
IPv6: fd00:1234:5678:9abc::1     # Unique local
IPv6: 2001:0:ce49:7601:e866:efff:62c3:fffe
IPv6: 1234:5678:9abc:def0:1234:5678:9abc:def0

**API Keys / Secrets**
Secret (Google API): AIzaSyA-abcdefgHIJKLMNOPQRSTUVWXYZ1234567890
Secret (Azure App): 6bc1bee22e409f96e93d7e117393172a
Secret (Slack token): xoxb-123456789012-1234567890123-AbCdEfGhIjKlMnOpQrStUvWx
Secret (JWT, very short): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
Secret (Firebase): AAAA12345:APA91bGHijklmNOPQRSTuvWXyZ
Secret (Random, high entropy): p@ssW0rd!@#%&*()_+|}{:?><
Secret (AWS Secret Access Key): wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Secret (Twilio Auth Token): 2b0b8a9be9b5edb3c45ad4eb23f8b675
Secret (GitLab token): glpat-abcdefghijklmno12345678
Secret (ServiceNow): 1d553d74c1e14f3f9a09d1aa232e0a1f

**Sensitive URL**
URL: https://secure.example.com/admin?access_token=eyJhbGciOiJIUzI1NiIs...
URL: https://app.prod-server.io/auth/reset?secret=9d8e7f6g5h4j3k2l1m0n9o8p7q6r5s4t
URL: https://login.example.net/callback?code=AQAAAAEAac6KAAAA
URL: https://internal.corp.org/api/v1/users?api_key=sk_live_abcdEfGh123456
URL: http://localhost:8080/dashboard?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9
URL: https://api.payments.com/refund?credit_card=4929123456789012
URL: ftp://files.example.org/private?token=s3cr3t
URL: https://cloud.vendor.com/v2/export?auth_token=AKIAIOSFODNN7EXAMPLE

**False Positives (Should NOT be detected)**
Not a CC: 123456789012345
Not a Phone: 555-ABC-9999
Not a MAC: 123456:789abc
Not an IPv4: 999.0.0.1
Not a Secret: totally_legit_secret
Not a Sensitive URL: https://localhost:3000/welcome
Not an IPv6: 2001:db8:zzzz::1
Not a MAC: 0G:00:00:00:00:00   # Invalid hex chars
Not an Email: user@@domain.com
Not a Phone: +123 (Not enough digits)


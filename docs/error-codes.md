# element save/create error-codes

## generic

  * **1**: marked as not to be None
  * **2**: marked as unique, but element with value <value\> allready present
  * **3**: needs to be of type <type\> [or None]

## session

  * **10***(user_id)*: There is no User with id '<user_id\>'
  * **11***(till)*: needs to be in the future
  * **12***(ip)*: does not match with the IP of request

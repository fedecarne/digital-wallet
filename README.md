# Antifraud.py: Insight Data Engineering coding challenge

1. [Dependencies] (README.md#dependencies)
2. [Problem summary] (README.md#problem-summary)
3. [Features] (README.md#features)
5. [Details of implementation] (README.md#details-of-implementation)
3. [Extra Features] (README.md#extra-features)
6. [Performance] (README.md#timing)
7. [Tests] (README.md#tests)

##Dependencies

To run Antifraud.py, please install the following libraries:

+ numpy: sudo apt-get install python-numpy
+ scipy: sudo apt-get install python-scipy

##Problem summary

PayMo is a "digital wallet" company that allows users to easily request and make payments to other PayMo users. This code implements features to prevent fraudulent payment requests from untrusted users.

## Features

###Feature 1

When anyone makes a payment to another user, they'll be notified if they've never made a transaction with that user before.

* "unverified: You've never had a transaction with this user before. Are you sure you would like to proceed with this payment?"

###Feature 2

Allow payments to a "friend of a friend". For example, User A has never had a transaction with User B, but both User A and User B have made transactions with User C, so User B is considered a "friend of a friend" for User A.

###Feature 3
Allow payments to friends up to 4th degrees apart. Warn users only when they're outside the "4th degree friends network".

##Details of implementation

Antifraud uses the history of PayMo transactions to define the 'user network'. The history of transactions is stored in the .csv file "batch_payments".

The code implements a modified bidirectional [Breadth-First search](https://en.wikipedia.org/wiki/Breadth-first_search) algorithm (BFS) to check, given two arbitrary users, whether their degree of separation is greater than a given degree threshold (*d*). Setting this threshold to 1, 2 or 4, implements Feature 1, Feature 2 or Feature 3, respectively.

The implementedd search is bidirectional, starting at both nodes and iterating alternatively between them. Also, this modified BFS algorithm is faster than a regular BFS in that it does not need to complete the search: If the search iteration has reached depth=*d* without finding a match, then we know that these users are out of a *d*th degree network and we should raise a warning.

##Extra Features

###Feature 4: Strength of friendship
The fundamental assumption behind Features 1-3 is that the network of payments  reflects, to some extent, the real social network of the users. This is, of course, an approximation. A and B might be friends in real life but have not done any transaction between them through PayMo. Because unnecessary warnings are annoying, we want to minimize 'false alarms' (wrongly raised warnings in transactions between friends). Therefore, any way to better infer the social network from the payment network would be beneficial for our cause.

One way to better infer the social network from the payment network is to assume that the frequency of payments reflect 'strength of friendship'. That is, if A and B have done many transactions between them, it is more likely that they know each other well than if they had only made a few. We can also assume that if A and B are really good friends, it is more likely that A will know B's friends than if they were only acquaintances. Therefore, a fraud detection algorithm that takes into account strength of friendship will be better at inferring the true social network and produce less amount of 'false alarm' warnings.

####Implementation:

Feature 4 creates a weighted graph from the batch payment file in which the weights between each pair of user is inversely proportional to the number of transaction that they have made between them. 

Given this weighted graph, for every new transaction the shortest distance between the users is computed and if this distance is greater than a certain threshold, a warning is raised. Because the graph is weighted by the number of transactions (strength of friendship), warnings will not be raised for users separated by larger degrees compared to Features 1-3, provided that the users between them are "good friends".

Feature 4 implements [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Algorithm) with priority queues to efficiently find the shortest path between users. Then simply uses this distance to evaluate whether the transaction is or not trusted. To increase speed, if during the search the distance threshold is crossed, the search is aborted and the transaction is marked as unverified.

###Feature 5: User model (statistical testing of transaction's amount)
A general approach in detecting fraudulent transactions involves having a model of the normal behavior of the user and compare every new transaction with the predictions of this model. This is useful because a fraudulent event would likely depart from the user's regular behavior and therefore can be detected by this comparison.

Mathematically, this can be achieved by statistically testing the hypothesis that a given transaction is fraudulent versus the null hypothesis that it is a trusted transaction. The statistical model can be as sophisticated as we want, provided there is enough data.  For simplicity, in this code we assume that the user behavior is Gaussian: that is, the amount of payments follows a normal distribution. The parameters of this distribution are different for each user and are obtained from the payment's history log (batch_payment.txt).

####Implementation

Feature 5 uses a [Smirnov-Grubbs test](https://en.wikipedia.org/wiki/Grubbs%27_test_for_outliers) with 0.05% significance level to asses the likelihood of fraud of every transaction. Smirnov-Grubbs is a statistical test to detect outliers in data sets assumed to come from a normal distribution. If the test's result is positive it rises a warning of possible fraud event.

##Performance

The code was tested in a Intel® Core™ i7-5500U CPU @ 2.40GHz × 4 with 8Gb of memory under Ubuntu 14.04.

Features 1 and 2 take less than 50 microseconds per transaction. Features 3 and 4 take less than 150 microseconds per transaction to be computed.
Feature 5 takes less than 20 microseconds per transaction.

The code includes some functions to compute the current state of the network (*extract_users*, *edge_to_adj*, *generate_w_adj_list* and *compute_stats*) that take significant more time. However, in a final implementation the state of the network would be updated online as new transactions arrive.

##Tests

### Known values: (test-known-values)

Tests basic functionality using a small batch_payment and stream_payment files and known values of trusted/unverified transactions.

### Unknown users: (test-unknown-values)

Tests the case when one or more users in a transaction are new to PayMo. That is, users in stream_payment file that are not present in batch_payment. Because they are new (they have no PayMo friends yet), their first transaction will always be unverified for Features 1-4. Feature 5 (statistical model) has no applicability to new users - given that there is no data to infer a model- so it does nor raise a warning.

### Test statistical model: (test-stats)

Tests different scenarios for Feature 5 (statistical model). Transactions in which a user pays more than what he/she has usually paid before (should be warned). Transactions in which a user pays a similar amount to what he/she has paid before should not be warned (should not be warned).

### Test weighted graph: (test-weighted)

Test designed for Feature 4, with a small history of payments including many repeated transactions between users. Users with many repeated transactions between them are assumed to be 'more' friends that pairs with less repeated transactions. Therefore transactions with the same degree of separation might or not be warned depending on the strength of friendship between users.













# Task
How would you test that the API between
the embedded and the cloud is working as
expected without having the real physical device
# Answer
The best option here to have mock of firmware, so there will be no need to have electronics part.
Embedded and firmware mock will be installed in virtualized OS. Firmware mock should have API to be controlled 
by test logic, so test engineers will be able to emulate different test cases.
Let say we want to test that embedded send proper request to cloud in case of electronics fill overheat.
In that case we should set firmware mock to send signal to embedded about such problem, so the embedded will send request to cloud.
By spoofing traffic between embedded and cloud we will be able to verify correctness of API. 

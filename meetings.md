# Meetings notes

## Meeting 1.
* **DATE: 1.2.2024**
* **ASSISTANTS: Iván Sánchez Milara**

### Minutes
In the meeting, the current version of the API description was discussed in a somewhat detailed manner. Overall, the current API description appeared a bit too technical and detailed considering the requirements set for the content at this moment. The API description is strongly focused on the functionalities and implementation of the project, and while these aspects were considered relevant, they are actually meant to be addressed later during the project. The content presented in the meeting is therefore relevant and will not need to be removed, but instead transferred elsewhere to be provided later on during the project. Finally, additional content regarding the overview, the main concepts as well as the related work of the project was requested to clarify the fundamental aspects of the project.

### Action points
1. Include motivation, e.g. possible customers and achievable benefits of the API in *Section 1: API overview*. 
2. Instead of functionalities, describe the general concepts of the API and include a diagram describing the relations between them in *Section 2: Main concepts*.
3. Include an example of a service that would utilize the API in *Section 3: API uses*.
4. Provide links to the related API examples and classify them according to the instructions in *Section 4: Related work*.

## Meeting 2.
* **DATE: 21.2.2024**
* **ASSISTANTS: Iván Sánchez Milara**

### Minutes
The discussion points in the meeting were mainly about the progress of the database design and implementation. Overall the content was ok. The README.md file did not include facts such as how to create and populate a database although the required files are attached to the repository. Since there are usernames and passwords are involved in the 'Admin' table, the API authentication should be considered during the DB implementation. The relationship between the 'Booking' to 'Room' should be changed since a single booking can have only one room. If a customer is to book multiple rooms, multiple bookings are to be made. There are many types of rooms and for validation of room types, JSON Schema or validation in API level can be used. The 'Booking' table has two unique attributes and it was discussed to use a single number as the unique ID. 

### Action points
1. The instructions about how to create and deploy the database are to be added to the README.md file.
2. The 'Booking' to 'Room' relationship to be changed to many-to-one.
3. The 'booking_ref' attribute is to be used as the primary key of the 'Booking' table. 

## Meeting 3.
* **DATE: 25.3.2024**
* **ASSISTANTS: Iván Sánchez Milara**

### Minutes
The meeting was held at 13:00 at Mr.Iván's office. The purpose of the meeting was to discuss the progress in the API implementation. The resource table and the addressability feature were OK. Then we discussed how the uniform interface feature can be explained more with examples. The file structure can be improved more with dividing into separate files. The code quality was above 9/10 in all of the files. The instruction was not added on how to run the test. The testing and implementation is to check in the next meeting. 

### Action points
1. The uniform interface section is required to be updated with the examples for each method.
2. The code should be arranged according to the project structure.
3. The instructions should be there on how the API testing is done.
4. The test coverage is needed to be improved.
5. The implementation is yet to present to the teacher. 




## Meeting 4.
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*




## Midterm meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*




## Final meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*





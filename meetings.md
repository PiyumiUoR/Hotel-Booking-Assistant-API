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
The purpose of the meeting was to assess the progress of the group regarding the API implementation. The resources and the required features of a REST API were considered appropriate with the exception of the uniform interface that lacked examples of the different request types. The file structure can be improved more by separating it into separate files. The Pylint score describing the quality of the code was excellent. Instructions on how to run tests for the API were not added in README. The schema validation, converters, and authentication were implemented appropriately as additional features. The testing and implementation demonstration will be checked in the next meeting.

### Action points
1. The uniform interface section needs to be updated with examples for each method.
2. The code may be arranged according to the project structure for improvement. 
3. The instructions on testing the API need to be provided in README.
4. The test coverage needs to be improved, particularly for the main application.
5. The implementation and corresponding test coverage will be demonstrated in the next meeting.

## Meeting 4.
* **DATE: 10.4.2024**
* **ASSISTANTS: Iván Sánchez Milara**

### Minutes
The purpose of this meeting was to evaluate the hypermedia implementation and documentation of our API. Hypermedia was assessed based on its relation diagram and the corresponding implementation. The primary idea of a hypermedia diagram was clarified in the meeting, and a new diagram with all the connected resources will be drawn based on the feedback. The API documentation presented in the meeting was identified as somewhat outdated as it described the API prior to any hypermedia implementation. The API tests presented in this meeting considered only the status codes, not the hypermedia responses. The mandatory query parameters for getting rooms with the RoomCollection resource were considered slightly problematic. In other words, the API could be a bit broader and allow client-side filtering instead. In conclusion, both the documentation and testing need to be updated before the final meeting to correctly represent the hypermedia implementation.

### Action points
1. Utilize IANA terms in the namespace when applicable (e.g. *edit* instead of *modify-booking*)
2. The hypermedia diagram needs to be updated to represent the resources and their connectedness properly
3. In the CustomerItem resource, the hypermedia should not provide a control for adding a customer
4. The query parameters in the RoomCollection resource should be optional, not mandatory
5. Testing needs to be updated to consider hypermedia responses in addition to the status codes

## Final meeting
* **DATE: 17.5.2024**
* **ASSISTANTS: Iván Sánchez Milara**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*





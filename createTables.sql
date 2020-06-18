CREATE TABLE tbl_students (
	studentID serial primary key,
	email varchar(250),
	firstName varchar(30),
	lastName varchar(30)
);


CREATE TABLE tbl_groups (
    groupID serial primary key,
    name character varying(50),
    description character varying(300)
);


CREATE TABLE tbl_groupsStud (
	studentID int references tbl_students,
	groupID int references tbl_groups,
	primary key(studentID, groupID)
);
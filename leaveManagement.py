import pyodbc
from datetime import date

class User:
    def __init__(self, user_name, user_email, position, leave_balances, on_leave):
        self.user_name = user_name
        self.user_email = user_email
        self.position = position
        self.leave_balances = leave_balances
        self.on_leave = on_leave

class LeaveType:
    def __init__(self, leave_type, max_days):
        self.leave_type = leave_type
        self.max_days = max_days

class LeaveApplication:
    def __init__(self, user_id, leave_type_id, start_date, end_date, total_days, destination, destination_add, ro_id, status, submit_date, co_id):
        self.user_id = user_id
        self.leave_type_id = leave_type_id
        self.start_date = start_date
        self.end_date = end_date
        self.total_days = total_days
        self.destination = destination
        self.destination_add = destination_add
        self.ro_id = ro_id
        self.status = status
        self.submit_date = submit_date
        self.co_id = co_id

class ReportingOfficer:
    def __init__(self, name, officer_email, department):
        self.name = name
        self.officer_email = officer_email
        self.department = department

class CoveringOfficer:
    def __init__(self, name, co_officer_email, department):
        self.name = name
        self.officer_email = co_officer_email
        self.department = department

# no need first
class Approver:
    def __init__(self, user_id, approver_email, name):
        self.user_id = user_id
        self.approver_email = approver_email
        self.name = name

class LeaveManagement:
    def __init__(self, server, database):
        self.connection = pyodbc.connect(f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database}")
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    # for Leave Applicant part
    def apply_leave(self, leaveDetails):
        if leaveDetails.co_id is not None:
            query = f"INSERT INTO leave_applications (user_id, leave_type_id, start_date, end_date, total_days, destination, destination_add, ro_id, status, submit_date, co_id) VALUES ({leaveDetails.user_id}, {leaveDetails.leave_type_id}, CONVERT(DATE, '{leaveDetails.start_date}', 23), CONVERT(DATE, '{leaveDetails.end_date}', 23), {leaveDetails.total_days}, '{leaveDetails.destination}', '{leaveDetails.destination_add}', {leaveDetails.ro_id}, '{leaveDetails.status}', CONVERT(DATE, '{leaveDetails.submit_date}',23), {leaveDetails.co_id} )"
        else:
            query = f"INSERT INTO leave_applications (user_id, leave_type_id, start_date, end_date, total_days, destination, destination_add, ro_id, status, submit_date) VALUES ({leaveDetails.user_id}, {leaveDetails.leave_type_id}, CONVERT(DATE, '{leaveDetails.start_date}', 23), CONVERT(DATE, '{leaveDetails.end_date}', 23), {leaveDetails.total_days}, '{leaveDetails.destination}', '{leaveDetails.destination_add}', {leaveDetails.ro_id}, '{leaveDetails.status}', CONVERT(DATE, '{leaveDetails.submit_date}',23))"
        self.cursor.execute(query)
        self.connection.commit()

    def amend_leave(self, user_change_id, selection):

        # fetch first
        query = f"SELECT * FROM leave_applications WHERE user_id = {user_change_id}"
        self.cursor.execute(query)
        user_data = self.cursor.fetchone()

        if selection == 1:
            c_start_date = input("Please enter the Start Date. : ")
            query = f"UPDATE leave_applications SET start_date = CONVERT(DATE, '{c_start_date}') WHERE user_id = {user_change_id}"
            print("Changes made.")
            self.cursor.execute(query)
            self.connection.commit()
        elif selection == 2:
            c_end_date = input("Please enter the End Date. : ")
            query = f"UPDATE leave_applications SET end_date = CONVERT(DATE, '{c_end_date}') WHERE user_id = {user_change_id}"
            print("Changes made.")
            self.cursor.execute(query)
            self.connection.commit()
        elif selection == 3:
            c_total_day = input("Please enter the total day. : ")
            query = f"UPDATE leave_applications SET total_days = {c_total_day} WHERE user_id = {user_change_id}"
            print("Changes made.")
            self.cursor.execute(query)
            self.connection.commit()
        elif selection == 4:
            if user_data.co_id is None:
                c_decision_co = input("Previous selection don't have Covering Officer (CO), do you want to sent to CO ? (Y/N) : ").lower()
                if c_decision_co == 'y':
                    #view co
                    self.view_co()
                    co_id = int(input("Enter the Covering officer ID : "))
                    query = f"UPDATE leave_applications SET co_id = {co_id} WHERE user_id = {user_change_id}"
                    print("Changes made.")
                    self.cursor.execute(query)
                    self.connection.commit()
                else:
                    print("No changes made.")
            else:
                # view co
                self.view_co()
                c_co_id = int(input("Enter the Covering Officer ID : "))
                query = f"UPDATE leave_applications SET co_id = {c_co_id} WHERE user_id = {user_change_id}"
                print("Changes made.")
                self.cursor.execute(query)
                self.connection.commit()
        elif selection == 5:
            self.view_ro()
            c_ro_id = input("Please enter the Reporting Officer ID : ")
            query = f"UPDATE leave_applications SET ro_id = {c_ro_id} WHERE user_id = {user_change_id}"
            print("Changes made.")
            self.cursor.execute(query)
            self.connection.commit()
        else:
            print("Please enter only 1-5")

    def cancel_leave(self, leave_application_id):
        confirmation = input("Do you sure want to cancel leave ? (Y/N)").lower()
        if confirmation == "y":
            query = f"DELETE from leave_applications WHERE leave_application_id={leave_application_id}"
            self.cursor.execute(query)
            self.connection.commit()

    def view_on_leave_staff(self):
        query = f"SELECT * FROM users WHERE on_leave = 'y'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.connection.commit()

        if len(rows) == 0:
            print("No staff on leave. ")
        else:
            print("On leave staff")
            print("---------------")
            for i, row in enumerate(rows):
                print(f"User_id: {row[0]} - Name: {row[1]} - Email: {row[2]} - Position: {row[3]}")

    def view_leave_balance(self, user_id):

        # fetch first
        query = f"SELECT * FROM users WHERE user_id = {user_id}"
        self.cursor.execute(query)
        user_data = self.cursor.fetchone()

        if user_data.leave_balances <= 0:
            print("No leave balance left.")
        else:
            print("Leave Balance left: " + str(user_data.leave_balances))

        self.cursor.execute(query)
        self.connection.commit()

    def view_leave_history(self, user_id):
        query = f"SELECT l.leave_type, la.start_date, la.end_date, la.total_days, la.destination, la.submit_date " \
                f"FROM leave_applications la " \
                f"JOIN leave_types l ON la.leave_type_id = l.leave_type_id " \
                f"WHERE user_id = {user_id}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            print("No leave taken before.")
        else:
            print("Leave History\n---------------")
            for i, row in enumerate(rows):
                print(
                    f"Leave_Type: {row.leave_type} - Start_Date: {row.start_date} - End_Date: {row.end_date} - Total_days: {row.total_days} - destination: {row.destination} - submit_date: {row.submit_date}")


   # for Approval part
    def approve_leave(self, leave_application_id):
        approve = "Approve"
        reject = "Reject"
        query = f"SELECT * FROM leave_applications WHERE leave_application_id = {leave_application_id}"
        self.cursor.execute(query)
        user_data = self.cursor.fetchone()

        # fetch from user table
        query2 = f"SELECT leave_balances FROM users WHERE user_id = {user_data[1]}"
        self.cursor.execute(query2)
        user_balance = self.cursor.fetchone()[0]

        print("1. Approve\n"
              "2. Reject ")
        selection = int(input("Please enter 1 for approve or 2 to reject : "))

        if selection == 1:
            #total_day
            if user_data[5] > user_balance:
                print("Insufficient leave balance.")
                return

            #update the leave
            query = f"UPDATE leave_applications SET status = '{approve}' WHERE leave_application_id = {leave_application_id}"
            self.cursor.execute(query)
            self.connection.commit()

            #update the leave balance
            new_balance = user_balance - user_data[5]
            query2 = f"UPDATE users SET leave_balances = {new_balance} WHERE user_id = {user_data[1]}"
            self.cursor.execute(query2)
            self.connection.commit()
            print("Leave Approved")

        elif selection == 2:
            query = f"UPDATE leave_applications SET status = '{reject}' WHERE leave_application_id = {leave_application_id}"
            print("Leave Rejected")
            self.cursor.execute(query)
            self.connection.commit()
        else:
            print("Invalid selection. Only key in 1 or 2")

    # Viewing for Approver leave history has been approved.
    def view_leave_approver_application(self):
        query = "SELECT * FROM leave_applications WHERE status = 'Approve'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if len(rows) == 0:
              print("No application found")
        else:
            print("Leave Application List")
            print("---------------------------------")
            for i, row in enumerate(rows):
                   print(
                       f"Leave_App_ID: {row.leave_application_id} - user_id: {row.user_id} - leave_type_id: {row.leave_type_id} - start_date: {row.start_date} - end_date: {row.end_date} - total_days: {row.total_days} - ro_id: {row.ro_id} - co_id: {row.co_id} - status: {row.status} - Submit Date: {row.submit_date}")


    # for viewing user/applicant purpose only
    def view_user(self):
        query = "SELECT * FROM users"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            print("No user found")
        else:
            print("Users")
            print("----------")
            for i, row in enumerate(rows):
                print(f"{row.user_id} - {row.user_name} - {row.user_email} - {row.position} ") # - {row.leave_balances} - {row.on_leave}

    # for viewing type of leaves only
    def view_type_of_leave(self):
        query = "SELECT * FROM leave_types"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            print("No data found")
        else:
            print("Type of Leave")
            print("--------------")
            for i, row in enumerate(rows):
                print(f"{row.leave_type_id} - {row.leave_type} ") # - {row.max_days}

    # for viewing Reporting officer only
    def view_ro(self):
        query = "SELECT * FROM officers_table"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            print("No officer found")
        else:
            print("Reporting Officer List")
            print("------------------------")
            for i, row in enumerate(rows):
                print(f"{row.ro_id} - {row.name} - {row.officer_email} - {row.department}")

    # for viewing Covering officer only
    def view_co(self):
        query = "SELECT * FROM co_officers_table"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            print("No CO officer found")
        else:
            print("Reporting Covering Officer List")
            print("---------------------------------")
            for i, row in enumerate(rows):
                print(f"{row.co_id} - {row.name} - {row.co_officer_email} - {row.department}")

    # for viewing Covering officer only
    def view_approver(self):
        query = "SELECT * FROM approver_table"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            print("No CO officer found")
        else:
            print("Approver List")
            print("---------------------------------")
            for i, row in enumerate(rows):
                print(f"{i+1}.{row.approver_id} - {row.approver_email} - {row.name} ")

    # for viewing the leave_application
    def view_leave_application(self):
        query = "SELECT * FROM leave_applications"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            print("No application found")
        else:
            print("Leave Application List")
            print("---------------------------------")
            for i, row in enumerate(rows):
                print(f"Leave_App_ID: {row.leave_application_id} - user_id: {row.user_id} - leave_type_id: {row.leave_type_id} - start_date: {row.start_date} - end_date: {row.end_date} - total_days: {row.total_days} - ro_id: {row.ro_id} - co_id: {row.co_id} - status: {row.status} - Submit Date: {row.submit_date}")



def main():
    server = "(localdb)\LocalDB"
    database = "leave"

    leaveManagement = LeaveManagement(server, database)

    while True:
        print("Welcome to Leave Application")
        print("1. Leave Application\n"
              "2. Leave Approval")

        choice = int(input("Please enter your choice (1-2): "))

        if choice == 1:
            print("Leave Application\n"
                  "-------------------\n"
                  "1. Apply Leave \n"
                  "2. Save as draft first\n"
                  "3. Amend Leave / Edit Leave \n"
                  "4. Cancel Leave\n"
                  "5. View Staff on leave\n"
                  "6. View Leave Balance\n"
                  "7. View Leave History\n"
                  "8. Quit")

            choice1 = int(input("Please enter your choice (1-7): "))

            if choice1 == 1:
                # view the list of user table

                leaveManagement.view_user()

                user_id = int(input("Please enter the user id : "))

                # view leave type
                leaveManagement.view_type_of_leave()
                leave_type_id = int(input("Please enter the leave type id : "))
                start_date = input("Please enter leave start date in YYYY-MM-DD format : ")
                end_date = input("Please enter leave end date in YYYY-MM-DD format : ")
                total_days = int(input("Please enter the total day : "))
                destination = input("Enter the destination : ")
                destination_add = input("Enter the destination address : ")

                # view the list of reporting officer
                leaveManagement.view_ro()
                ro_id = int(input("Enter the Reporting officer ID : "))
                co_confirm = input("Do you want to send to Covering Officer? (Y/N):").lower()

                co_id = None

                if co_confirm == "y":
                    # view the list of Co officer
                    leaveManagement.view_co()
                    co_id = int(input("Enter the Covering officer ID : "))
                else:
                    pass

                # view the list of approver
                #leaveManagement.view_approver()
                #approver_id = int(input("Enter the Approver ID : "))
                status = input("Enter the status (Pending, Approved): ")
                submit_date = date.today()

                leaveApplication = LeaveApplication(user_id, leave_type_id, start_date, end_date,
                                                    total_days, destination, destination_add, ro_id,
                                                    status, submit_date, co_id)
                leaveManagement.apply_leave(leaveApplication)
                print("Leave Applied.")
            elif choice1 == 2:
                # save as draft
                print("This part not yet done")
            elif choice1 == 3:
                # amend/edit details ( should view the application, instead of user )
                leaveManagement.view_leave_application()
                user_change_id = int(input("Which user do you want to amend ? : "))
                print("1. Start Date\n"
                      "2. End Date\n"
                      "3. Total Day\n"
                      "4. Change CO\n"
                      "5. Change RO\n")
                selection = int(input("Which part do you want to amend ? :"))

                leaveManagement.amend_leave(user_change_id, selection )
            elif choice1 == 4:
                leaveManagement.view_leave_application()
                leave_application_id = int(input("Which leave_application_id want to cancel leave ? :"))
                leaveManagement.cancel_leave(leave_application_id)
            elif choice1 == 5:
                leaveManagement.view_on_leave_staff()
            elif choice1 == 6:
                leaveManagement.view_user()
                user_id = int(input("Which user do you want to check leave balance? :"))
                leaveManagement.view_leave_balance(user_id)
            elif choice1 == 7:
                leaveManagement.view_user()
                user_id = int(input("Which user do you want to check its leave history? :"))
                leaveManagement.view_leave_history(user_id)
            else:
                print("Invalid Input, only 1-8 selection available.")

        # Approval part
        if choice == 2:
            print("Leave Approval\n"
                  "-------------------\n"
                  "1. Approve Leave \n"
                  "2. View Leave History \n"
                  "3. Quit")

            choice2 = int(input("Please enter your choice (1-4): "))

            if choice2 == 1:
                # view the leave_application
                leaveManagement.view_leave_application()
                application_id = int(input("Please enter the leave_application_id to be approved \ reject :"))
                leaveManagement.approve_leave(application_id)
            elif choice2 == 2:
                leaveManagement.view_leave_approver_application()
            else:
                print("Invalid Input, only 1-3 selection available.")

if __name__=='__main__':
    main()
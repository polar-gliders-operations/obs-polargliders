

# EXPORT CONTROLLED - This technology or software is subject to the U.S. Export Administration
# Regulations (EAR), (15 C.F.R. Parts 730-774). No authorization from the U.S. Department of
# Commerce is required for export, re-export, in-country transfer, or access EXCEPT to country
# group E:1 or E:2 countries/persons per Supp. 1 to Part 740 of the EAR.

# Copyright © 2011,2021 Liquid Robotics, Inc., confidential and proprietary. All rights reserved.

# Python script to utilize the WGMS Data Service.
#
# The script utilizes the zeep module which can be installed by:
#   pip3 install zeep
#
# Zeep provides an easy to use programmatic interface to a 
# SOAP server.

# Author: Theja Kanumury
# Email: theja.kanumury@liquid-robotics.com
# Version: 1.0.0

# Importing modules.
from datetime import datetime, timedelta
from zeep import Client, helpers
import argparse
import time


# Report list
# ["Raw Data Report","Telemetry 6 Report","Amps Power Summary Report","Amps Output Power Status Report","Amps Solar Input Port Report","Amps Battery Port Report","Amps Bridge Power Port Report","Telemetry 6 Report by WGMS Datetime","Raw Data Report by WGMS DateTime","Tracker Report","AIS Report","Vehicle Error Report","Data Usage Report"]
# 
# Platforms IDs
# SV3-052: 2107397055
# TRACKER-0042: 946244935



# Constants. TODO: move to a config file
wsdl            = "https://dataservice.wgms.com/WDS/WGMSData.asmx?wsdl" # Data Service WSDL URL                                          
org             = "csir"                                               # WGMS Org
user            = "datauser"                                      # WGMS Org user
password        = "dataAccount007"                                          # WGMS Org Password
reportName      = "Telemetry 6 Report"                                    # Data to be sent back 
resultFormat    = 1                                                     # Default Option 

# Creating a zeep client to the WGMS Data Service WSDL
client = Client(wsdl)

# Function to convert zeep object to a JSON format.
def convertToJSON(zeepOutput, result):
    jsonFormat = zeepOutput.__values__.get(result)
    print(jsonFormat)

# Function to get list of gliders in the specified org.
def getGliderList():
    # Calling WGMS Data Service to get the list of gliders. 
    zeepOutput = client.service.GetGliderList(org, 
        User = user, 
        Password = password, 
        ResultFormat = resultFormat) 
    gliderList = convertToJSON(zeepOutput, "GetGliderListResult")

# Function to get list of reports that can be requested.
def getReportList():
    # Calling WGMS Data Service to get a list of reports.
    zeepOutput = client.service.GetReportList(org, 
        User = user, 
        Password = password, 
        ResultFormat = resultFormat)
    reportList = convertToJSON(zeepOutput, "GetReportListResult")

# Function to get data from a specified vehicle within a specified time frame.
def getReportData(startDate, endDate, vehicles):
    if vehicles == "":
        with client.settings(strict=False):
            # Calling WGMS Data Service to get data from all vehicles in org 
            zeepOutput = client.service.GetReportData(Org = org, 
                User = user, 
                Password = password, 
                ReportName = reportName, 
                StartDate = startDate, 
                EndDate = endDate, 
                ResultFormat = resultFormat)
            reportData = convertToJSON(zeepOutput, "GetReportDataResult")
    else:
        for vehicle in vehicles:
            # Calling WGMS Data Service to get data from specified vehicles in org 
            zeepOutput = client.service.GetReportData(org, 
                User = user, 
                Password = password, 
                ReportName = reportName, 
                SerialNo = vehicle, 
                StartDate = startDate, 
                EndDate = endDate, 
                ResultFormat = resultFormat)
            # Converting zeepOutput to a JSON format
            reportData = convertToJSON(zeepOutput, "GetReportDataResult")

# Function to get data at specified intervals over a time.
def getPeriodicData(interval, period, vehicles):    
    startTime = datetime.now()
    print("Started requesting data from " 
        + str(startTime)
        + " onwards at an interval of " 
        + str(interval)
        + " minute(s) for "
        + str(period) 
        + " minutes.")
    # Loop to request data during the specified length of time.
    while True:
        now = datetime.now()
        intervalTimeAgo = now - timedelta(minutes = interval)
        startDate = intervalTimeAgo.strftime("%Y-%m-%d" + "T" + "%H:%M:%S" + "Z")
        endDate = now.strftime("%Y-%m-%d" + "T" + "%H:%M:%S" + "Z")
        print("Getting data between " + startDate + " & " + endDate)
        getReportData(startDate, endDate, vehicles)
        if datetime.now() >= startTime + timedelta(minutes = period):
            break
        else:
            # Calculating sleep time to avoid drift.
            sleepTime = ((interval*60) 
            - (int(datetime.now().strftime("%S")) - int(startTime.strftime("%S"))) 
            % (interval*60))
            time.sleep(sleepTime)
    print("Stopped getting data at " + str(datetime.now()))

# Function to check if specified date is in the right format.
def validDate(input):
    try:
        return datetime.strptime(input, "%Y-%m-%d" + "T" + "%H:%M:%S" + "Z")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(input) + "\nRequired Format: YYYY-mm-DDTHH:MM:SSZ"
        raise argparse.ArgumentTypeError(msg)

def main():
    # Defining user inputs to the script.
    parser = argparse.ArgumentParser(description = 
        "Python script to utilize the WGMS Data Service.")
    parser.add_argument("--getGliderList", action = "store_true", 
        help = "Command to get list of gliders in org.")
    parser.add_argument("--getReportList", action = "store_true", 
        help = "Command to get list of reports.")
    parser.add_argument("--getReportData", action = "store_true", 
        help = "Command to get raw data from a specified vehicle in a date range."
            + " Requires user to specify startDate and endDate.")
    parser.add_argument("--getPeriodicData", action = "store_true", 
        help = "Command to get data over a specified period of time at specified intervals." 
            + " Requires user to specify interval and time")
    parser.add_argument("--vehicles", nargs = "*", default = "",
        help = "The vehicle serial number. For multiple vehicle spaces needed between numbers."
            + "Example --vehicles 123 456 789")
    parser.add_argument("--startDate", type = validDate, 
        help = "Start date and time of the requested data. Format: YYYY-mm-DDTHH:MM:SSZ")
    parser.add_argument("--endDate", type = validDate, 
        help = "End date and time of the requested data. Format: YYYY-mm-DDTHH:MM:SSZ")
    parser.add_argument("--interval", type = int, 
        help = "Length of time interval in minutes.")
    parser.add_argument("--time", type = int, 
        help = "Length of time you want the python script to run in minutes.")
    args = parser.parse_args()

    if (args.getGliderList):
        getGliderList()
        exit()
    
    if (args.getReportList):
        getReportList()
        exit()

    if (args.getReportData):
        if not [var for var in (args.startDate, args.endDate) if var is None]:
            if args.endDate > args.startDate:
                getReportData(args.startDate, args.endDate, args.vehicles)   
                exit()
            else:
                print("The end date (--endDate) is earlier than the start date (--startDate).")
                exit()
        else:
            print("One or more of the required variables (--startDate, --endDate)"
                + " was not entered.")
            exit()

    if(args.getPeriodicData):
        if not [var for var in (args.interval, args.time) if var is None]:
            getPeriodicData(args.interval, args.time, args.vehicles)
            exit()
        else:
            print("One or more of the required variables (--interval, --time)" 
                + " was not entered.")
            exit()
    
if __name__ == "__main__":
    main()

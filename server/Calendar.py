from datetime import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
credentials_file = 'user_info/calendar/credentials.json'
token_file = 'user_info/calendar/token.json'
calendarId = 'v5bb5nfjci1u9l2ajddht2cta4@group.calendar.google.com'


class CalendarController:
    def __init__(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)

    def get_upcoming_events(self):
        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')

        events_result = self.service.events().list(calendarId=calendarId, timeMin=now,
                                                   maxResults=10, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events

    def get_event_info(self, event):
        """
        @TODO: Timezone aware datetime
        :param event:
        :return: dict with: - start & end: dates in Google Calendar timezone format.
                            - start_in & end_after: start job in start_in seconds for end_after seconds
                            - summary: Event title/summary string
        """
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        utc_start = datetime.strptime(self.get_utc_time(start), "%Y-%m-%dT%H:%M:%S")
        utc_end = datetime.strptime(self.get_utc_time(end), "%Y-%m-%dT%H:%M:%S")
        now = datetime.now()

        start_in = (utc_start - now).total_seconds()
        if start_in < 0:
            start_in = 0
            end_after = (utc_end - now).total_seconds()
        else:
            end_after = (utc_end - utc_start).total_seconds()

        return {'id': event['id'], 'summary': event['summary'],
                'start': start, 'end': end,
                'start_in': start_in, 'end_after': end_after}

    @staticmethod
    def get_utc_time(time_str):
        # TODO: This
        # Given a time_str in the format "2022-03-14T06:45:00-04:00", where -04:00 represents the timezone difference
        return time_str[:-6]
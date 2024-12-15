
FROM flink-base:latest

# install python3: it has updated Python to 3.9 in Debian 11 and so install Python 3.7 from source, \
# it currently only supports Python 3.6, 3.7 and 3.8 in PyFlink officially.

# add python script
USER flink
RUN pip3 install kafka-python

ADD stock_pipeline.py /opt/flink/usrlib/stock_pipeline.py
# ADD flink-sql-connector-kafka-3.1.0-1.18.jar /opt/flink/usrlib/flink-sql-connector-kafka-3.1.0-1.18.jar
# ADD flink-connector-jdbc-3.1.2-1.18-javadoc.jar /opt/flink/usrlib/flink-connector-jdbc-3.1.2-1.18-javadoc.jar
# ADD postgresql-42.2.27.jre6.jar /opt/flink/usrlib/postgresql-42.2.27.jre6.jar
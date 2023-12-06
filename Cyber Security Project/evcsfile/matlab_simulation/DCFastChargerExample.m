%% DC Fast Charger for Electric Vehicle
%
% This example models a DC fast charging station connected with the battery 
% pack of an Electric Vehicle (EV). 
%
% The main components of the example are:
%
% * Grid - Model the AC supply voltage as a three-phase constant voltage source.
% * DC Fast Charging Station - Model the power electronic circuits to
% convert the AC supply voltage from the grid to the DC voltage level that 
% the EV battery pack requires.
% * EV battery pack - Model the battery pack as series of battery cells.

% Copyright 2021-2023 The MathWorks, Inc.

%% Model Overview
open_system('DCFastCharger')
set_param(find_system('DCFastCharger','MatchFilter', @Simulink.match.allVariants, 'FindAll', 'on','type','annotation','Tag','ModelFeatures'),'Interpreter','off')

%% Components in DC Fast Charging Station
%
% These are the main components of the system:
%
% * Filter & AC Measurements to filter the harmonics in the line current and
% measure the three-phase supply voltage and line current.
%%
open_system('DCFastCharger/Filter & AC measurements')
set_param(find_system('DCFastCharger','MatchFilter', @Simulink.match.allVariants,'FindAll', 'on','type','annotation','Tag','ModelFeatures'),'Interpreter','off')

%%
% * Unity Power Factor (UPF) Front End Converter (FEC) to control output 
% DC voltage at 800 V.

%%
open_system('DCFastCharger/Front end converter')
set_param(find_system('DCFastCharger','MatchFilter', @Simulink.match.allVariants,'FindAll', 'on','type','annotation','Tag','ModelFeatures'),'Interpreter','off')

%%
% The converter circuit is modeled with three levels of fidelity:

%%
open_system('DCFastCharger/Front end converter/FEC')
set_param(find_system('DCFastCharger','MatchFilter', @Simulink.match.allVariants,'FindAll', 'on','type','annotation','Tag','ModelFeatures'),'Interpreter','off')

%%
% * Average Inverter Fidelity

%%
powerCircuit=0; %#ok<*NASGU> 
open_system('DCFastCharger/Front end converter/FEC/Average')
set_param(find_system('DCFastCharger','MatchFilter', @Simulink.match.allVariants,'FindAll', 'on','type','annotation','Tag','ModelFeatures'),'Interpreter','off')

%%
% * Two Level Inverter Fidelity

%%
powerCircuit=1;
sim('DCFastCharger');
open_system('DCFastCharger/Front end converter/FEC/Two Level')
set_param(find_system('DCFastCharger','MatchFilter', @Simulink.match.allVariants,'FindAll', 'on','type','annotation','Tag','ModelFeatures'),'Interpreter','off')

%%
% * Three Level Inverter Fidelity

%%
powerCircuit=2;
sim('DCFastCharger');
open_system('DCFastCharger/Front end converter/FEC/Three Level')
set_param(find_system('DCFastCharger','MatchFilter', @Simulink.match.allVariants,'FindAll', 'on','type','annotation','Tag','ModelFeatures'),'Interpreter','off')

%%
% * Isolated DC-DC converter supply constant charging current to the EV battery.
%%
open_system('DCFastCharger/DC-DC converter with galvanic isolation')
set_param(find_system('DCFastCharger','MatchFilter', @Simulink.match.allVariants,'FindAll', 'on','type','annotation','Tag','ModelFeatures'),'Interpreter','off')

%%
% These are the main components of the isolated DC-DC Converter:
% * Inverter

%%
open_system('DCFastCharger/DC-DC converter with galvanic isolation/Inverter')
set_param(find_system('DCFastCharger','MatchFilter', @Simulink.match.allVariants,'FindAll', 'on','type','annotation','Tag','ModelFeatures'),'Interpreter','off')

%%
% * HF Isolation Transformer

%%
open_system('DCFastCharger/DC-DC converter with galvanic isolation/HF isolation transformer')
set_param(find_system('DCFastCharger','MatchFilter', @Simulink.match.allVariants,'FindAll', 'on','type','annotation','Tag','ModelFeatures'),'Interpreter','off')

%%
% * Diode-Bridge Rectifier

%%
open_system('DCFastCharger/DC-DC converter with galvanic isolation/Diode-Bridge rectifier')
set_param(find_system('DCFastCharger','MatchFilter', @Simulink.match.allVariants,'FindAll', 'on','type','annotation','Tag','ModelFeatures'),'Interpreter','off')

%% EV Battery Pack Overview
% The EV Battery Pack models the battery cells connected in series and the 
% sensors to measure the battery terminal voltage and output current. 

%%
file_path = 'received_messages_CP_1.txt';
output_path = 'data_mod.txt';

% Open the input file in read mode
fid = fopen(file_path, 'r');
SoC = [];
i=1;

% Check if the file is opened successfully
if fid == -1
    error('Unable to open the file.');
end

try
    % Open the output file in write mode
    fid_out = fopen(output_path, 'w');

    % Check if the output file is opened successfully
    if fid_out == -1
        error('Unable to open the output file.');
    end

    try
        % Read each line in the file
        lineCounter = 0;
     
        while ~feof(fid)
            % Read a line from the file
            line = fgetl(fid);
            
            % Increment line counter
            lineCounter = lineCounter + 1;

            % Skip the first line (header)
            if lineCounter == 1
                continue;
            end

            % Split the line into timestamp and message using strsplit
            parts = strsplit(line, ' - ');
            
            if numel(parts) == 2
                timestamp_str = parts{1};
                message_str = parts{2};

                % Convert timestamp string to datetime object
                timestamp_vec = datevec(timestamp_str, 'HH:MM:SS');
                timestamp = datetime([2023, 5, 12, timestamp_vec(4:6)]);

                % Display the timestamp for debugging
                disp(['Timestamp: ' char(timestamp)]);

                % Replace single quotes with double quotes in the message string
                message_str = strrep(message_str, "'", '"');

                % Use jsondecode to convert the message string to a structure
                message_struct = jsondecode(message_str);
                
                % Update the 'capacity' value to 40
                SoC(i)= message_struct.custom_data.capacity;
                i=i+1;

                % Print the updated timestamp and capacity for debugging
                %disp(['Updated Timestamp: ' char(timestamp)]);
                %disp(['SoC Level: ' num2str(message_struct.custom_data.capacity)]);

                % Convert the updated message structure back to a string
                updated_message_str = jsonencode(message_struct);

                % Write the updated line to the output file
                fprintf(fid_out, '%s - %s\n', timestamp_str, updated_message_str);
            else
                % If the line doesn't have the expected format, write it as is
                fprintf(fid_out, '%s\n', line);
            end
            
        end
        i=1;

        disp(['File has been modified and saved to: ' output_path]);

    catch
        % Close the output file in case of an error
        fclose(fid_out);
        rethrow(lasterror);
    end

    % Close the output file
    fclose(fid_out);

catch
    % Close the input file in case of an error
    fclose(fid);
    rethrow(lasterror);
end

disp(SoC(length(SoC)))


battery.initialSOC= SoC(length(SoC))/100;

open_system('DCFastCharger/EV Battery')
set_param(find_system('DCFastCharger','MatchFilter', @Simulink.match.allVariants,'FindAll', 'on','type','annotation','Tag','ModelFeatures'),'Interpreter','off')

%% Simulation Results from Simscape Logging
%
% The plot below shows the DC bus voltage and current, battery terminal 
% voltage, and charging current.

powerCircuit=0;
open_system('DCFastCharger/Scope : DCFastCharger');
sim('DCFastCharger');

%%







#https://bitbucket.org/uscsoftwareengineering/lustreutils/raw/cb0673a13688c96c3e47eb9f4e0bc221ba123f5e/LustreUtils/experimentBase/extractTestCase.awk
# Originally written by Greg Gay
# copied at Apr 24 2017 by Taejoon Byun
BEGIN{
	values[0]=0;

	# Get list of inputs
	split(I,inputs,",");

	numInputs=0;
	for(i in inputs){
		numInputs++;
	}

	# Read in report and extract test case
	invalid=0;
	inputVars=0;
	while(getline x < F){
		if(x ~ /INVALID/){
			invalid=1;
			# Get number of test steps
			split(x,parts," ");
			steps=parts[9];
			# Set default value of 0 for all inputs
			for(input=1;input<=numInputs;input++){
				values[input]="";
				for(step=1;step<=steps;step++){
					values[input]=values[input] "0,";
				}
				values[input]=substr(values[input],1,length(values[input])-1);
			}
		}else if(x ~ /INPUTS/){
			if(invalid==1){
				inputVars=1;
			}else{
				print "NOT AN INVALID PROPERTY";
			}
		}else if(x ~ /OUTPUTS/){
			# Stop when we get to outputs.
			break;
		}else if(inputVars==1){
			# Extract values for that input variable
			split(x,parts," ");
			numParts=0;
			for(p in parts){
				numParts++;
			}
			for(input=1;input<=numInputs;input++){
				if(parts[1]==inputs[input]){
					val="";
					for(part=2;part<=numParts;part++){
						if(parts[part]!=""){
							if(parts[part]=="true"){
								val=val "true,";
							}else if(parts[part]=="false"){
								val=val "false,";
							}else if(parts[part]=="-"){
								val=val "0,";
							}else{
								val=val parts[part] ",";
							}
						}
					}
					values[input]=substr(val,1,length(val)-1);
				}
			}
		}
	}
	close(F);

	# Form test cast
	for(step=1;step<=steps;step++){
		testCase[step]="";
	}
	for(input=1;input<=numInputs;input++){
		split(values[input],vals,",");
		for(step=1;step<=steps;step++){
			testCase[step] = testCase[step] vals[step] ",";
		}
	}
	for(step=1;step<=steps;step++){
		print substr(testCase[step],1,length(testCase[step])-1);
	}
}

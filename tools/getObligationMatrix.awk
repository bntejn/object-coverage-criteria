BEGIN{

	result[0]=0;
	line=1

	while(getline x < F){
		if(x==""){
			out="";
			for(i=1;i<=Obligations;i++){
				if(result[i]!=1)
					result[i]=0;

				out=out","result[i];
				result[i]=0;
			}
			print substr(out,2);
		}else if(line!=1){
			split(x,parts,",");
			for(i=1;i<=Obligations;i++){
				if(parts[i]=="false"){
					result[i]=1;
				}
			}	
		}else{
			print x;
		}	
		line++;
	}
	close(F);
}

BEGIN{

	result[0]=0;
	line=1

	while(getline x < F){
		split(x,parts,",");
		for(i=1;i<=Obligations;i++){
			if(parts[i]==0){
				result[i]=1;
			}
		}	
	}
	close(F);

	fulfilled=0;
	unfulfilled=0;
	for(i=1;i<=Obligations;i++){
		if(result[i]==1){
			fulfilled++;
		}else{
			unfulfilled++;	
		}
	}

	print fulfilled","unfulfilled;
}

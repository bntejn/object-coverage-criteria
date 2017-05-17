# not used
function get_cols_to_keep {
    # get columns to keep
    cols=`cat $1/$sys/$base.lus | awk ' 
        BEGIN{
            discard=0
            var[0]=0
        }
        {
            if($0 ~ /returns/) {
                discard=1;
            }
            if(($0 ~ /:/) && (discard==0)){
                var[++var[0]]=$0;
            }
        }
        END{
            cols="";
            skip=0;
            for(i=1; i<=var[0]; i++) {
                if(var[i] ~ /returns/) {
                    skip=1;
                } 
                var[i]=substr(var[i],0,index(var[i],":")-1);
                if(var[i] ~ /[(]/){
                    var[i] =substr(var[i],index(var[i],"(")+1,length(var[i]));
                }
                if(!skip){
                    cols=cols var[i] ","
                }
            }
            print substr(cols,0,length(cols)-1)
        }
    '`
}


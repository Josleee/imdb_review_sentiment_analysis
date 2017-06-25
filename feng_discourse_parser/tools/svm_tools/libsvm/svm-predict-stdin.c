#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include "svm.h"

char* line;
int max_line_len = 1024;
struct svm_node *x;
int max_nr_attr = 64;

struct svm_model* model;
int predict_probability=0;

void predict_stdin()
{
	int correct = 0;
	int total = 0;
	double error = 0;
	double sumv = 0, sumy = 0, sumvv = 0, sumyy = 0, sumvy = 0;

	int svm_type=svm_get_svm_type(model);
	int nr_class=svm_get_nr_class(model);
	double *prob_estimates=NULL;
	int j;

	if(predict_probability)
	{
		if (svm_type==NU_SVR || svm_type==EPSILON_SVR)
			printf("Prob. model for test data: target value = predicted value + z,\nz: Laplace distribution e^(-|z|/sigma)/(2sigma),sigma=%g\n",svm_get_svr_probability(model));
		else
		{
			
			int *labels=(int *) malloc(nr_class*sizeof(int));
			svm_get_labels(model,labels);
			prob_estimates = (double *) malloc(nr_class*sizeof(double));
			/*
			fprintf(output,"labels");		
			for(j=0;j<nr_class;j++)
				fprintf(output," %d",labels[j]);
			fprintf(output,"\n");
			free(labels);
			*/
		}
	}
	
	printf("Ready for input:\n");
	fflush(stdout);

	while(1)
	{
		int i = 0;
		int c;
		double target,v;
		
		c = getc(stdin);
		if (c == '\n')
			break;
		else
		{
			//printf("# %c", c);
			ungetc(c, stdin);
		}
		

		scanf("%lf",&target);
		
		while(1)
		{
			if(i>=max_nr_attr-1)	// need one more for index = -1
			{
				max_nr_attr *= 2;
				x = (struct svm_node *) realloc(x,max_nr_attr*sizeof(struct svm_node));
			}

			do {
				c = getc(stdin);
				if(c=='\n' || c==EOF) goto out2;
			} 
			while(isspace(c));
			
			ungetc(c,stdin);
			
			
			if (scanf("%d:%lf",&x[i].index,&x[i].value) < 2)
			{
				fprintf(stderr,"Wrong input format at line %d\n", total+1);
				exit(1);
			}
			++i;
		}
		


out2:
		x[i].index = -1;

		if (predict_probability && (svm_type==C_SVC || svm_type==NU_SVC))
		{
			v = svm_predict_probability(model, x, prob_estimates);

			printf("%g ",v);
			for(j=0;j<nr_class;j++)
				printf("%g ",prob_estimates[j]);
			printf("\n");
		}
		else
		{
			v = svm_predict(model,x);
			printf("%g\n",v);
		}

		if(v == target)
			++correct;
		error += (v-target)*(v-target);
		sumv += v;
		sumy += target;
		sumvv += v*v;
		sumyy += target*target;
		sumvy += v*target;
		++total;
		
		fflush(stdout);
	}
	if (svm_type==NU_SVR || svm_type==EPSILON_SVR)
	{
		printf("Mean squared error = %g (regression)\n",error/total);
		printf("Squared correlation coefficient = %g (regression)\n",
		       ((total*sumvy-sumv*sumy)*(total*sumvy-sumv*sumy))/
		       ((total*sumvv-sumv*sumv)*(total*sumyy-sumy*sumy))
		       );
	}
	else
		printf("Accuracy = %g%% (%d/%d) (classification)\n",
		       (double)correct/total*100,correct,total);
	if(predict_probability)
		free(prob_estimates);
}

void exit_with_help()
{
	printf(
	"Usage: svm-predict [options] test_file model_file output_file\n"
	"options:\n"
	"-b probability_estimates: whether to predict probability estimates, 0 or 1 (default 0); for one-class SVM only 0 is supported\n"
	);
	exit(1);
}

int main(int argc, char **argv)
{
	int i;

	// parse options
	for(i=1;i<argc;i++)
	{
		if(argv[i][0] != '-') break;
		++i;
		switch(argv[i-1][1])
		{
			case 'b':
				predict_probability = atoi(argv[i]);
				break;
			default:
				fprintf(stderr,"unknown option\n");
				exit_with_help();
				break;
		}
	}
	if(i>=argc)
		exit_with_help();

	if((model=svm_load_model(argv[i]))==0)
	{
		fprintf(stderr,"can't open model file %s\n",argv[i]);
		exit(1);
	}

	line = (char *) malloc(max_line_len*sizeof(char));
	x = (struct svm_node *) malloc(max_nr_attr*sizeof(struct svm_node));
	if(predict_probability)
	{
		if(svm_check_probability_model(model)==0)
		{
			fprintf(stderr,"Model does not support probabiliy estimates\n");
			exit(1);
		}
	}
	else
	{
		if(svm_check_probability_model(model)!=0)
			printf("Model supports probability estimates, but disabled in prediction.\n");
	}

	predict_stdin();
	svm_destroy_model(model);
	free(line);
	free(x);
	return 0;
}

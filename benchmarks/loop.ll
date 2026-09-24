; ModuleID = 'loop.ll'
source_filename = "loop.ll"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@__lumina_argc = local_unnamed_addr global i32 0
@__lumina_argv = local_unnamed_addr global ptr null
@str_0 = local_unnamed_addr constant [1 x i8] zeroinitializer
@str_1 = local_unnamed_addr constant [3 x i8] c"%s\00"
@str_2 = local_unnamed_addr constant [2 x i8] c" \00"
@str_3 = constant [4 x i8] c"%ld\00"
@str_4 = local_unnamed_addr constant [2 x i8] c"\0A\00"

; Function Attrs: nofree nounwind
declare noundef i32 @printf(ptr nocapture noundef readonly, ...) local_unnamed_addr #0

declare void @GC_init() local_unnamed_addr

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i64 @strlen(ptr nocapture) local_unnamed_addr #1

declare i64 @atoi(ptr) local_unnamed_addr

declare i64 @clock() local_unnamed_addr

define noundef i32 @main(i32 %.1, ptr %.2) local_unnamed_addr {
main_entry:
  tail call void @GC_init()
  store i32 %.1, ptr @__lumina_argc, align 4
  store ptr %.2, ptr @__lumina_argv, align 8
  %argv_elem_ptr = getelementptr ptr, ptr %.2, i64 1
  %argv_elem = load ptr, ptr %argv_elem_ptr, align 8
  %len_str = tail call i64 @strlen(ptr noundef nonnull dereferenceable(1) %argv_elem)
  %icmp = icmp sgt i64 %len_str, 0
  br i1 %icmp, label %if_end, label %if_end.thread

if_end.thread:                                    ; preds = %main_entry
  %clock_call7 = tail call i64 @clock()
  br label %for_body.preheader

if_end:                                           ; preds = %main_entry
  %atoi_call = tail call i64 @atoi(ptr %argv_elem)
  %0 = add i64 %atoi_call, 1
  %clock_call = tail call i64 @clock()
  %for_cond.13 = icmp sgt i64 %0, 1
  br i1 %for_cond.13, label %for_body.preheader, label %for_end

for_body.preheader:                               ; preds = %if_end.thread, %if_end
  %clock_call10 = phi i64 [ %clock_call7, %if_end.thread ], [ %clock_call, %if_end ]
  %n.09 = phi i64 [ 100000001, %if_end.thread ], [ %0, %if_end ]
  br label %for_body

for_body:                                         ; preds = %for_body.preheader, %for_body
  %storemerge5 = phi i64 [ %for_next, %for_body ], [ 1, %for_body.preheader ]
  %spec.store.select24 = phi i64 [ %spec.store.select, %for_body ], [ 0, %for_body.preheader ]
  %add.1 = add i64 %spec.store.select24, %storemerge5
  %mul = mul i64 %storemerge5, %clock_call10
  %icmp.1 = icmp slt i64 %mul, 0
  %spec.store.select = select i1 %icmp.1, i64 0, i64 %add.1
  %for_next = add nuw nsw i64 %storemerge5, 1
  %exitcond.not = icmp eq i64 %for_next, %n.09
  br i1 %exitcond.not, label %for_end, label %for_body

for_end:                                          ; preds = %for_body, %if_end
  %spec.store.select2.lcssa = phi i64 [ 0, %if_end ], [ %spec.store.select, %for_body ]
  %putchar = tail call i32 @putchar(i32 32)
  %print_call.1 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @str_3, i64 %spec.store.select2.lcssa)
  %putchar1 = tail call i32 @putchar(i32 10)
  ret i32 0
}

; Function Attrs: nofree nounwind
declare noundef i32 @putchar(i32 noundef) local_unnamed_addr #0

attributes #0 = { nofree nounwind }
attributes #1 = { mustprogress nofree nounwind willreturn memory(argmem: read) }
